import os
import sys
import json
import random
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../py_protobuf")))

from Location_pb2 import TrackPartType
from scenario_generator import ScenarioGenerator,ScenarioGeneratorHIP
from random_generator import RandomGenerator


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Name of configuration file for the scenario generation.", required=False, default="examples/example_config1.json")
parser.add_argument("-s", "--scenario-file", help="Optional custom name of created scenario file.", required=False, default=None)


def create_scenario_from_config(config_file, scenario_file):
    config = json.load(open(os.path.join(os.path.dirname(__file__), config_file), "r"))
    correct_file, config = check_configuration_file(config)
    if not correct_file:
        exit()

    scenario_generator = ScenarioGenerator()
    scenario_generator.load_location(config["location_file"])
    scenario_generator.add_start_and_end_times(config["start_time"], config["end_time"])
    if config['trains_given']:
        correct_file, config = check_train_details_file(config, scenario_generator.location)
        if not correct_file:
            exit()

    if "seed" in config:
        random_generator = RandomGenerator(scenario_generator, config["seed"], scenario_generator.location)
    else:
        config["seed"] = 42
        random_generator = RandomGenerator(scenario_generator, 42, scenario_generator.location)

    if config["use_default_material"]:
        scenario_generator.add_DefaultTrainUnitTypes()
        random_generator.train_unit_types = scenario_generator.scenario_TrainUnitTypes.copy()
    else:
        random_generator.generate_train_unit_types(config["number_of_train_unit_types"])

    services = {}
    if config["perform_servicing"]:
        for service in config["custom_servicing_tasks"]:
            task_type = scenario_generator.create_TaskType(None, service["type"])
            service_obj = scenario_generator.create_TaskSpec(task_type, service["priority"], service["duration"], service["required_skills"])
            services[service["name"]] = service_obj

    if config["trains_given"]:
        created_train_units = {}
        for train_unit in config["custom_train_units"]:
            unit = scenario_generator.create_TrainUnit(train_unit["id"], train_unit["type"], [services[s] for s in train_unit["services"]])
            created_train_units[train_unit["id"]] = unit
        for train in config["custom_trains"]:
            if "arrival_track" in train:
                scenario_generator.add_incomingTrain(
                    scenario_generator.create_Train(
                        id=train["id"], 
                        members=[created_train_units[i] for i in train["members"]], 
                        time=train["arrival_time"], 
                        trackPart=train["arrival_track"],
                        sideTrackPart=train["arrival_track_side"]
                    )
                )
            if "departure_track" in train:
                # TODO does this work? double train units created
                unmatched_train_units = [scenario_generator.create_TrainUnitUnmatchedMembers(train_unit) for train_unit in train["member_types"]]
                scenario_generator.add_outgoingTrain(
                    scenario_generator.create_Train(
                        id=train["id"], 
                        members=unmatched_train_units,
                        time=train["departure_time"], 
                        trackPart=train["departure_track"],
                        sideTrackPart=train["departure_track_side"],
                        canDepartFromAnyTrack=train["depart_any_track"] if "depart_any_track" in train else False
                    )
                )
            if "start_at_track" in train:
                scenario_generator.add_inStandingTrain(
                    scenario_generator.create_Train(
                        id=train["id"], 
                        time=0,
                        members=[created_train_units[i] for i in train["members"]], 
                        trackPart=train["start_at_track"],
                        sideTrackPart=train["start_at_track_side"],
                        standingIndex=train["parking_index"] if "parking_index" in train else 1
                    )
                )                
            if "end_at_track" in train:
                scenario_generator.add_outStandingTrain(
                    scenario_generator.create_Train(
                        id=train["id"], 
                        time=0,
                        members=[created_train_units[i] for i in train["members"]], 
                        trackPart=train["end_at_track"],
                        sideTrackPart=train["end_at_track_side"],
                        standingIndex=train["parking_index"] if "parking_index" in train else 1
                    )
                )    
    else:
        random_generator.generate_train_compositions(config, scenario_generator)
    
    if config["through_traffic_given"]:
        pass
    if config["partial_plan_given"]:
        pass
    if config["partial_matching_given"]:
        pass
    
    scenario_generator_hip = ScenarioGeneratorHIP(scenario_generator)
    scenario_generator.create_HIP_scenario()

    if not scenario_file or not os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "..", "data", "scenarios", f"{scenario_file}.json")):
        num_trains = len(config["custom_trains"]) if config["trains_given"] else config["number_of_trains"]
        custom = f"custom" if config["trains_given"] else f"random_{config['seed']}s"
        scenario_file = f"scenario_{config['location']}_{num_trains}t_{custom}_{config_file.split('/')[-1].split('_')[-1].split('.')[0]}"
    output_filepath = os.path.join(os.path.dirname(__file__), "..", "..", "data", "scenarios", f"{scenario_file}.json")
    output_hip_filepath = os.path.join(os.path.dirname(__file__), "..", "..", "data", "scenarios", f"{scenario_file}_hip.json")
    # Write TORS scenario file
    scenario_generator.save_scenario_json(output_filepath)
    # Write HIP scenario file
    scenario_generator_hip.save_scenario_json(output_hip_filepath)
    # Update HIP location file
    scenario_generator.convert_location_to_hip_location(os.path.join(os.path.dirname(__file__), "..", "..", "data", "locations", config["location_file"].replace(".json", "_hip.json")))    


    

def check_configuration_file(config):
    if "location" not in config:
        print("ERROR: 'location' not defined.")
        return False, config
    if not os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "..", "data", "locations", f'location_{config["location"]}.json')):
        print("ERROR: could not find location file.", f'location_{config["location"]}.json')
        return False, config
    else:
        config["location_file"] = f"location_{config['location']}.json"
    if "start_time" not in config:
        print("ERROR: 'start_time' not defined.")
        return False, config
    if "end_time" not in config:
        print("ERROR: 'end_time' not defined.")
        return False, config
    if "use_default_material" not in config:
        print("ERROR: 'use_default_material' not defined.")
        return False, config
    if "trains_given" not in config:
        print("ERROR: 'trains_given' not defined.")
        return False, config
    if not config["use_default_material"]:
        if config["trains_given"] or "custom_train_units" in config or "custom_trains" in config or "custom_servicing_tasks" in config:
            print("ERROR: cannot specify custom train units, trains, and servicing tasks for randomly generated material.")
            return False, config
        if "number_of_train_unit_types" not in config:
            print("ERROR: no 'number_of_train_unit_types' defined while train unit types should be generated ('use_default_material' is false)")
            return False, config
    else:
        default_train_unit_names = [unit["name"] for unit in json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "data", "train_unit_types.json")))]
    if config["trains_given"] and ("custom_train_units" not in config or "custom_trains" not in config):
        print("ERROR: no 'custom_train_units' or 'custom_trains defined' while 'trains_given' is true.")
        return False, config
    if not config["trains_given"] and ("number_of_trains" not in config or "number_of_train_units" not in config):
        print("ERROR: no 'number_of_trains' or 'number_of_train_units' defined while trains and train units should be generated ('trains_given' is false).")
        return False, config
    if not config["trains_given"] and "train_unit_distribution" in config:
        if "units_per_composition" not in config["train_unit_distribution"]:
            print("ERROR: no 'units_per_composition' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "type_ratio" not in config["train_unit_distribution"]:
            print("ERROR: no 'type_ratio' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "matching_complexity" not in config["train_unit_distribution"]:
            print("ERROR: no 'matching_complexity' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "train_unit_types" in config["train_unit_distribution"]:
            if not config["use_default_material"]:
                print("ERROR: 'train_unit_types' defined in the 'train_unit_distribution' while 'use_default_material' was false, cannot specify specify unit types for randomly generated unit types.")
                return False, config
            for t in config["train_unit_distribution"]["train_unit_types"]:
                if t not in default_train_unit_names:
                    print(f"ERROR: 'train_unit_distribution' defined 'train_unit_types' with an unknown train unit type {t}.")
    if "perform_servicing" not in config:
        print("ERROR: 'perform_servicing' not defined.")
        return False, config
    if config["perform_servicing"] and "custom_servicing_tasks" not in config:
        print("WARNING: no 'custom_servicing_tasks' found")
    if "partial_matching_given" not in config:
        config["partial_matching_given"] = False
    if "partial_plan_given" not in config:
        config["partial_plan_given"] = False
    if "through_traffic_given" not in config:
        config["through_traffic_given"] = False
    if config["through_traffic_given"] and "custom_through_traffic" not in config:
        print("WARNING: no 'custom_through_traffic' found")
    if config["partial_plan_given"] and "partial_plan" not in config:
        print("WARNING: no 'partial_plan' found")
    if config["partial_matching_given"] and "partial_matching" not in config:
        print("WARNING: no 'partial_matching' found")
    # TODO check other custom objects
    return True, config


def check_train_details_file(config, location):
    if "track_ids_used" not in config:
        print("WARNING: 'track_ids_used' not specified, assuming ids are used")
        config["custom_trains"]["track_ids_used"] = True
    default_train_unit_names = [unit["name"] for unit in json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "data", "train_unit_types.json")))]        
    for i, t in enumerate(config["custom_train_units"]):
        if "id" not in t or "type" not in t or "services" not in t:
            print(f"ERROR: incorrectly specified the {i}th custom train unit: missing id, type or service parameter")
            return False, config
        if t["type"] not in default_train_unit_names:
            print(f"ERROR: custom train unit with id {t['id']} has unknown type {t['type']}")
            return False, config
    train_units_check = {u["id"]: u["type"] for u in config["custom_train_units"]}
    train_units_check = {u["id"]: u["type"] for u in config["custom_train_units"]}
    track_names_to_ids = {track.name: int(track.id) for track in location.trackParts}
    if config["trains_given"]:
        for i, train in enumerate(config["custom_trains"]):
            if "id" not in train:
                print(f"ERROR: incorrectly specified the {i}th custom train: missing id")
                return False, config
            if "members" not in train and "member_types" not in train:
                print(f"ERROR: incorrectly specified the {i}th custom train: missing members or member_types")
                return False, config
            if "members" in train:
                member_type_check = set()
                for u in train["members"]:
                    if u not in train_units_check:
                        print(f"ERROR: train {train['id']} has member {u} that is not defined or already used in a different train composition")
                        return False, config
                    member_type_check.add(train_units_check[u].split("-")[0])
                    train_units_check.pop(u)
                if len(member_type_check) > 1:
                    print(F"WARNING: train {train['id']} has members from different train unit types: {member_type_check}")
            if "member_types" in train:
                member_type_check = set([mem.split("-")[0] for mem in train["member_types"]])
                if len(member_type_check) > 1:
                    print(F"WARNING: train {train['id']} has members from different train unit types: {member_type_check}")
            if "arrival_track" not in train and "start_at_track" not in train:
                print(f"WARNING: no 'arrival_track' or 'start_at_track' defined for train {train['id']}")
            if "departure_track" not in train and "end_at_track" not in train:
                print(f"WARNING: no 'departure_track' or 'end_at_track' defined for train {train['id']}")
            # Check if tracks exist in the location
            # Add the parking track parts: the track defined in the file is the actual track (used as parking track), but we also need the connected bumper
            correct, config = check_track_part_in_train(config, train, "arrival_track", track_names_to_ids, location, i, True)
            if not correct:
                return False, config
            correct, config = check_track_part_in_train(config, train, "departure_track", track_names_to_ids, location, i, True)
            if not correct:
                return False, config
            correct, config = check_track_part_in_train(config, train, "end_at_track", track_names_to_ids, location, i, False)
            if not correct:
                return False, config
            correct, config = check_track_part_in_train(config, train, "start_at_track", track_names_to_ids, location, i, False)
            if not correct:
                return False, config
            print(i, train)
    return True, config


def check_track_part_in_train(config, train, track_name, track_names_to_ids, location, i, arrival_departure):
    if track_name in train:
        if arrival_departure and track_name.replace("track", "time") not in train:
            print(f"ERROR: no '{track_name}' given for train {train['id']}")
            return False, config
        track_id = 0
        if config["track_ids_used"]:
            track_id = int(train[track_name])
        else:
            if train[track_name] in track_names_to_ids:
                track_id = track_names_to_ids[train[track_name]]
            else:
                print(f"ERROR: '{track_name}' {train[track_name]} not found in location {config['location']}")
                return False, config
        ### Find the side track part: either defined, a bumper or random connected track part
        config["custom_trains"][i][track_name] = track_id
        if "side_track_part" in train:
            if config["track_ids_used"]:
                side_id = int(train["side_track_part"])
            else:
                if train["side_track_part"] in track_names_to_ids:
                    side_id = track_names_to_ids[train["side_track_part"]]
                else:
                    print(f"ERROR: 'side_track_part' {train['side_track_part']} of {track_name} for train {train['id']} not found in location {config['location']}")
                    return False, config
        else:
            try:
                bumper_a = [location.trackParts[a].id 
                            for a in location.trackParts[track_id].aSide 
                            if location.trackParts[a].type == TrackPartType.Bumper]
                bumper_b = [location.trackParts[a].id 
                            for a in location.trackParts[track_id].bSide 
                            if location.trackParts[a].type == TrackPartType.Bumper]
                if len(bumper_a + bumper_b) != 1:
                    print(f"WARNING: no bumper found for '{track_name}' for train {train['id']}, picking random `side_track_part'")
                    sides = [location.trackParts[a].id for a in location.trackParts[track_id].aSide] + [location.trackParts[a].id for a in location.trackParts[track_id].bSide]
                    side_id = random.choice(sides)
                else:
                    side_id = (bumper_a + bumper_b)[0]
            except KeyError as e:
                print(f"ERROR: invalid '{track_name}' for train {train['id']}: {e} not found")
                return False, config
        config["custom_trains"][i][f"{track_name}_side"] = side_id
    return True, config
        


if __name__ == "__main__":
    args = parser.parse_args()
    create_scenario_from_config(args.config, args.scenario_file)

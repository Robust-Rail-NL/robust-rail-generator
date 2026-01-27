import os
import json
import logging
import random
from py_protobuf import Location_pb2
from google.protobuf.json_format import ParseDict

def check_configuration_file(config, location_path):
    """Checks basic parts of the configuration file to be present"""
    if not os.path.isfile(location_path):
        logging.error(f"Could not find location file '{location_path}'.")
        return False, config
    else:
        config["location_file"] = location_path
        res, config = check_location_file(config)
        if not res:
            return False, config
    if "start_time" not in config:
        logging.error("Not defined: 'start_time'.")
        return False, config
    if "end_time" not in config:
        logging.error("Not defined: 'end_time'.")
        return False, config
    if "use_default_material" not in config:
        logging.error("Not defined: 'use_default_material'.")
        return False, config
    if "trains_given" not in config:
        logging.error("Not defined: 'trains_given'.")
        return False, config
    if not config["use_default_material"]:
        if config["trains_given"] or "custom_train_units" in config or "custom_trains" in config or "custom_servicing_tasks" in config:
            logging.error("Cannot specify custom train units, trains, and servicing tasks for randomly generated material.")
            return False, config
        if "number_of_train_unit_types" not in config:
            logging.error("No 'number_of_train_unit_types' defined while train unit types should be generated ('use_default_material' is false)")
            return False, config
    else:
        default_train_unit_names = [unit["name"] for unit in json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "default_train_unit_types.json")))]
    if config["trains_given"] and ("custom_train_units" not in config or "custom_trains" not in config):
        logging.error("No 'custom_train_units' or 'custom_trains defined' while 'trains_given' is true.")
        return False, config
    if "number_of_trains" not in config:
        if not config["trains_given"]:
            logging.error("No 'number_of_trains' defined while trains and train units should be generated ('trains_given' is false).")
            return False, config
        else:
            config["number_of_trains"] = len([train for train in config["custom_trains"] if "arrival_track" in train or "start_at_track" in train])
    if not config["trains_given"] and "train_unit_distribution" in config:
        if "units_per_composition" not in config["train_unit_distribution"]:
            logging.error("No 'units_per_composition' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "super_type_ratio" not in config["train_unit_distribution"]:
            logging.error("No 'super_type_ratio' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "train_unit_types" in config["train_unit_distribution"]:
            if not config["use_default_material"]:
                logging.error("Defined 'train_unit_types' in the 'train_unit_distribution' while 'use_default_material' was false, cannot specify specify unit types for randomly generated unit types.")
                return False, config
            for t in config["train_unit_distribution"]["train_unit_types"]:
                if t not in default_train_unit_names:
                    logging.error(f"Defined 'train_unit_distribution' and 'train_unit_types' with an unknown train unit type {t}.")
                    return False, config
    if not config["trains_given"]:
        if "mixed_traffic" in config:
            if not isinstance(config["mixed_traffic"], bool):
                logging.error("'mixed_traffic' should be a boolean (true/false).")
                return False, config
        else:
            config["mixed_traffic"] = True
        if "matching" in config:
            if not isinstance(config["matching"], int) or config["matching"] not in [0, 1, 2]:
                logging.error("'matching' should be a value (0, 1, 2).")
                return False, config
        else:
            config["matching"] = 1
    if "min_time_in_yard" in config:
        if not isinstance(config["min_time_in_yard"], int) or config["min_time_in_yard"] < 0:
            logging.error("'min_time_in_yard' should be a non-negative integer.")
            return False, config
    else:
        config["min_time_in_yard"] = 600
    if "min_gap_on_gateway" in config:
        if not isinstance(config["min_gap_on_gateway"], int) or config["min_gap_on_gateway"] < 0:
            logging.error("'min_gap_on_gateway' should be a non-negative integer.")
            return False, config
    else:
        config["min_gap_on_gateway"] = 300
    # TODO Consider the servicing time
    if config["end_time"] - config["start_time"] // config["min_gap_on_gateway"] < config["number_of_trains"] * 2.1:
        logging.warning(f"Not enough time to shunt all {config['number_of_trains']} trains within {config['end_time'] - config['start_time']} allowing a gap of {config['min_gap_on_gateway']}, results in {config['end_time'] - config['start_time'] // config['min_gap_on_gateway']} slots")
        return False, config
    if "perform_servicing" not in config:
        logging.error("Not defined: 'perform_servicing'.")
        return False, config
    if config["perform_servicing"] and "custom_servicing_tasks" not in config:
        logging.warning("No 'custom_servicing_tasks' found")
    if "partial_matching_given" not in config:
        config["partial_matching_given"] = False
    if "partial_plan_given" not in config:
        config["partial_plan_given"] = False
    if "through_traffic_given" not in config:
        config["through_traffic_given"] = False
    if config["through_traffic_given"] and "custom_through_traffic" not in config:
        logging.warning("No 'custom_through_traffic' found")
    if config["partial_plan_given"] and "partial_plan" not in config:
        logging.warning("No 'partial_plan' found")
    if config["partial_matching_given"] and "partial_matching" not in config:
        logging.warning("No 'partial_matching' found")
    # TODO check other custom objects
    return True, config
    
def check_location_file(config):
    location = json.load(open(config["location_file"]))
    try:
        ParseDict(location, Location_pb2.Location())
    except Exception as e:
        logging.error(f"Could not parse the location file {config['location_file']} to the correct Location format. Be careful not to use the `_solver` format, or use the converter.")
        logging.error(e)
        return False, config
    config["track_id_map"] = {int(t["id"]): t for t in location["trackParts"]}
    if len(config["track_id_map"]) != max(config["track_id_map"].keys()):
        logging.warning(f"The ids of the tracks are not correctly set, the ids should be increasing by one and unique.")
        return True, config
        # Code to overwrite the ids, not working yet, probably not needed
        logging.error(f"The ids will be adjusted and the file will be recreated starting at the minimum {min(map_tracks.keys())} with max id {len(map_tracks) + min(map_tracks.keys()) - 1}")
        new_ids = {}
        max_ids = sorted(list(map_tracks.keys()), reverse=True)
        for i in range(min(map_tracks.keys()), len(map_tracks) + min(map_tracks.keys())):
            if i not in map_tracks.keys():
                new_ids[max_ids.pop(0)] = i
        for old, new in new_ids.items():
            for j in range(len(location["trackParts"])):
                if location["trackParts"][j]["id"] == old:
                    location["trackParts"][j]["id"] == new
                location["trackParts"][j]["aSide"] = [new if a == old else a for a in location["trackParts"][j]["aSide"]]
                location["trackParts"][j]["bSide"] = [new if b == old else b for b in location["trackParts"][j]["bSide"]]
            for j in range(len(location["trackParts"])):
                if location["trackParts"][j]["id"] == old:
                    location["trackParts"][j]["id"] = new
        print(location)
        json.dump(location, open(config["location_filepath"].replace(".json", "_fixedIDs.json"), "w"), indent=4)
    return True, config

def check_train_details_file(config, location):
    if "track_ids_used" not in config:
        logging.warning("Not defined: 'track_ids_used', assuming ids are used")
        config["track_ids_used"] = True
    default_train_unit_names = [unit["name"] for unit in json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "default_train_unit_types.json")))]        
    for i, t in enumerate(config["custom_train_units"]):
        if "id" not in t or "type" not in t or "services" not in t:
            logging.error(f"Incorrectly specified the {i}th custom train unit: missing id, type or service parameter")
            return False, config
        if t["type"] not in default_train_unit_names:
            logging.error(f"Custom train unit with id {t['id']} has unknown type {t['type']}")
            return False, config
    train_units_check_arrival = {u["id"]: u["type"] for u in config["custom_train_units"]}
    train_units_check_departure = [u["type"] for u in config["custom_train_units"]]
    track_names_to_ids = {track.name: int(track.id) for track in location.trackParts}
    if config["trains_given"]:
        for i, train in enumerate(config["custom_trains"]):
            if "id" not in train:
                logging.error(f"Incorrectly specified the {i}th custom train: missing id")
                return False, config
            if "members" not in train and "member_types" not in train:
                logging.error(f"Incorrectly specified the {i}th custom train: missing members or member_types")
                return False, config
            if "member_types" in train and "members" in train:
                logging.error(f"Both 'members' and 'member_types' defined for train {train['id']}, only one should be defined")
                return False, config
            if "members" in train and ("departure_track" in train or "end_at_track" in train):
                logging.error(f"Outgoing or outstanding train {train['id']} has members defined, but should have member_types defined for the train request instead of specific member id")
                return False, config
            if "member_types" in train and ("arrival_track" in train or "start_at_track" in train):
                logging.error(f"Incoming or standing train {train['id']} has member_types defined, but should have members defined for the specific train members")
                return False, config
            if "members" in train:
                member_type_check = set()
                for u in train["members"]:
                    if u not in train_units_check_arrival:
                        logging.error(f"Train {train['id']} has member {u} that is not defined or already used in a different train composition")
                        return False, config
                    member_type_check.add(train_units_check_arrival[u].split("-")[0])
                    train_units_check_arrival.pop(u)
                if len(member_type_check) > 1:
                    logging.warning(f"Train {train['id']} has members from different train unit types: {member_type_check}")
            if "member_types" in train:
                for u in train["member_types"]:
                    if u not in train_units_check_departure:
                        logging.error(f"Train {train['id']} has member {u} that is not defined or already used in a different train composition")
                        return False, config
                    train_units_check_departure.remove(u)
                member_type_check = set([mem.split("-")[0] for mem in train["member_types"]])
                if len(member_type_check) > 1:
                    logging.warning(f"Train {train['id']} has members from different train unit types: {member_type_check}")
            if "arrival_track" not in train and "start_at_track" not in train:
                logging.warning(f"No 'arrival_track' or 'start_at_track' defined for train {train['id']}, picking random gateway track part")
            if "arrival_track" in train and "start_at_track" in train:
                logging.error(f"Both 'arrival_track' (train should arrive) and 'start_at_track' (train is already in yard) defined for train {train['id']}, only one should be defined")
            if "arrival_track" in train and "end_at_track" in train:
                logging.error(f"Both 'arrival_track' and 'end_at_track' defined for train {train['id']}, only one should be defined (create separate objects for in(standing) and out(standing) trains)")
            if "arrival_track" in train and "departure_track" in train:
                logging.error(f"Both 'arrival_track' and 'departure_track' defined for train {train['id']},only one should be defined (create separate objects for in(standing) and out(standing) trains)")
            if "departure_track" not in train and "end_at_track" not in train:
                logging.warning(f"No 'departure_track' or 'end_at_track' defined for train {train['id']}, picking random gateway track part")
            if "departure_track" in train and "end_at_track" in train:
                logging.error(f"Both 'departure_track' (train should depart) and 'end_at_track' (train should reamin in yard) defined for train {train['id']}, only one should be defined")
            if "departure_track" in train and "start_at_track" in train:
                logging.error(f"Both 'departure_track' and 'start_at_track' defined for train {train['id']}, only one should be defined (create separate objects for in(standing) and out(standing) trains)")
                return False, config
            if "departure_track" in train and "arrival_track" in train:
                logging.error(f"Both 'departure_track' and 'arrival_track' defined for train {train['id']}, only one should be defined (create separate objects for in(standing) and out(standing) trains)")
                return False, config
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
    return True, config


def check_track_part_in_train(config, train, track_name, track_names_to_ids, location, i, arrival_departure):
    """Checks the train's track part defined for arrival and departure. It has to be a track_part in the location file, that can be seen as the """
    if track_name in train:
        if arrival_departure and track_name.replace("track", "time") not in train:
            logging.error(f"No '{track_name}' given for train {train['id']}")
            return False, config
        track_id = 0
        if config["track_ids_used"]:
            track_id = int(train[track_name])
        else:
            if train[track_name] in track_names_to_ids:
                track_id = track_names_to_ids[train[track_name]]
            else:
                logging.error(f"Track '{track_name}' {train[track_name]} not found in location {config['location']}")
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
                    logging.error(f"Track 'side_track_part' {train['side_track_part']} of {track_name} for train {train['id']} not found in location {config['location']}")
                    return False, config
        else:
            try:
                bumper_a = [location.trackParts[a].id 
                            for a in location.trackParts[track_id].aSide 
                            if location.trackParts[a].type == Location_pb2.TrackPartType.Bumper]
                bumper_b = [location.trackParts[a].id 
                            for a in location.trackParts[track_id].bSide 
                            if location.trackParts[a].type == Location_pb2.TrackPartType.Bumper]
                if len(bumper_a + bumper_b) != 1:
                    logging.warning(f"No bumper found for '{track_name}' for train {train['id']}, picking random `side_track_part'")
                    sides = [location.trackParts[a].id for a in location.trackParts[track_id].aSide] + [location.trackParts[a].id for a in location.trackParts[track_id].bSide]
                    side_id = random.choice(sides)
                else:
                    side_id = (bumper_a + bumper_b)[0]
            except KeyError as e:
                logging.error(f"Invalid '{track_name}' for train {train['id']}: {e} not found")
                return False, config
        config["custom_trains"][i][f"{track_name}_side"] = side_id
    return True, config
        
def check_gateways(config, location, gateways):
    track_per_ids = {int(t.id): t for t in location.trackParts}
    if "arrival" in config["gateway"]:
        for arrive_id in config["gateway"]["arrival"]:
            arrive = track_per_ids.get(int(arrive_id), None)
            if arrive is None:
                print(f"ERROR: arrival gateway {arrive_id} not found in in location")
                return False, config
            if arrive.type != Location_pb2.TrackPartType.RailRoad:
                print(f"ERROR: arrival gateway {arrive_id} is not a railroad")
                return False, config
            if arrive.parkingAllowed:
                print(f"ERROR: arrival gateway {arrive_id} does allow parking")
                return False, config
            if not arrive.sawMovementAllowed:
                print(f"ERROR: arrival gateway {arrive_id} does not allow saw movements")
                return False, config
            if arrive.length == 0:
                print(f"ERROR: arrival gateway {arrive_id} has length 0")
                return False, config
            # Assert that the JSON is well-formed
            assert all(int(a) == a for a in arrive.aSide), "aSide must be represented as int, not string"
            assert all(int(b) == b for b in arrive.bSide), "bSide must be represented as int, not string"
            bumper_a = [track_per_ids[a]
                        for a in arrive.aSide 
                        if track_per_ids[a].type == Location_pb2.TrackPartType.Bumper]
            bumper_b = [track_per_ids[b]
                    for b in arrive.bSide 
                    if track_per_ids[b].type == Location_pb2.TrackPartType.Bumper]
            if len(bumper_a) == 1:
                gateways["arrival"].append((arrive, bumper_a[0]))
            elif len(bumper_b) == 1:
                gateways["arrival"].append((arrive, bumper_b[0]))
            else:
                print(f"ERROR: arrival gateway {arrive_id} does not have a bumper side")
                return False, config
    if "departure" in config["gateway"]:
        for depart_id in config["gateway"]["departure"]:
            depart = track_per_ids.get(int(depart_id), None)
            if depart is None:
                print(f"ERROR: departure gateway {depart_id} not found in in location")
                return False, config
            if depart.type != Location_pb2.TrackPartType.RailRoad:
                print(f"ERROR: departure gateway {depart_id} is not a railroad")
                return False, config        
            if depart.parkingAllowed:
                print(f"ERROR: departure gateway {depart_id} does allow parking")
                return False, config
            if not depart.sawMovementAllowed:
                print(f"ERROR: departure gateway {depart_id} does not allow saw movements")
                return False, config
            if depart.length == 0:
                print(f"ERROR: departure gateway {depart_id} has length 0")
                return False, config
            # Assert that the JSON is well-formed
            assert all(int(a) == a for a in depart.aSide), "aSide must be represented as int, not string"
            assert all(int(b) == b for b in depart.bSide), "bSide must be represented as int, not string"
            bumper_a = [track_per_ids[a]
                        for a in depart.aSide 
                        if track_per_ids[a].type == Location_pb2.TrackPartType.Bumper]
            bumper_b = [track_per_ids[b] 
                    for b in depart.bSide 
                    if track_per_ids[b].type == Location_pb2.TrackPartType.Bumper]
            if len(bumper_a) == 1:
                gateways["departure"].append((depart, bumper_a[0]))
            elif len(bumper_b) == 1:
                gateways["departure"].append((depart, bumper_b[0]))
            else:
                print(f"ERROR: departure gateway {depart_id} does not have a bumper side")
                return False, config
    return True, gateways

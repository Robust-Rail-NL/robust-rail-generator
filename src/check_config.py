import os
import json
import logging
import random
from py_protobuf.Location_pb2 import TrackPartType

def check_configuration_file(config, location_path):
    """Checks basic parts of the configuration file to be present"""
    if "location" not in config:
        logging.error("Not defined: 'location'.")
        return False, config
    if not os.path.isfile(os.path.join(location_path, f"{config['location']}.json")):
        logging.error(f"Could not find location file '{config['location']}.json' at '{location_path}'.")
        return False, config
    else:
        config["location_file"] = f"{config['location']}.json"
        config["location_filepath"] = os.path.isfile(os.path.join(location_path, f"{config['location']}.json"))
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
        default_train_unit_names = [unit["name"] for unit in json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "train_unit_types.json")))]
    if config["trains_given"] and ("custom_train_units" not in config or "custom_trains" not in config):
        logging.error("No 'custom_train_units' or 'custom_trains defined' while 'trains_given' is true.")
        return False, config
    if not config["trains_given"] and "number_of_trains" not in config:
        logging.error("No 'number_of_trains' defined while trains and train units should be generated ('trains_given' is false).")
        return False, config
    if not config["trains_given"] and "train_unit_distribution" in config:
        if "units_per_composition" not in config["train_unit_distribution"]:
            logging.error("No 'units_per_composition' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "type_ratio" not in config["train_unit_distribution"]:
            logging.error("No 'type_ratio' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "matching_complexity" not in config["train_unit_distribution"]:
            logging.error("No 'matching_complexity' defined while a 'train_unit_distribution' is provided and train units should be generated ('trains_given' is false).")
            return False, config
        if "train_unit_types" in config["train_unit_distribution"]:
            if not config["use_default_material"]:
                logging.error("Defined 'train_unit_types' in the 'train_unit_distribution' while 'use_default_material' was false, cannot specify specify unit types for randomly generated unit types.")
                return False, config
            for t in config["train_unit_distribution"]["train_unit_types"]:
                if t not in default_train_unit_names:
                    logging.error(f"Defined 'train_unit_distribution' and 'train_unit_types' with an unknown train unit type {t}.")
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


def check_train_details_file(config, location):
    if "track_ids_used" not in config:
        logging.warning("Not defined: 'track_ids_used', assuming ids are used")
        config["custom_trains"]["track_ids_used"] = True
    default_train_unit_names = [unit["name"] for unit in json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "train_unit_types.json")))]        
    for i, t in enumerate(config["custom_train_units"]):
        if "id" not in t or "type" not in t or "services" not in t:
            logging.error(f"Incorrectly specified the {i}th custom train unit: missing id, type or service parameter")
            return False, config
        if t["type"] not in default_train_unit_names:
            logging.error(f"Custom train unit with id {t['id']} has unknown type {t['type']}")
            return False, config
    train_units_check = {u["id"]: u["type"] for u in config["custom_train_units"]}
    train_units_check = {u["id"]: u["type"] for u in config["custom_train_units"]}
    track_names_to_ids = {track.name: int(track.id) for track in location.trackParts}
    if config["trains_given"]:
        for i, train in enumerate(config["custom_trains"]):
            if "id" not in train:
                logging.error(f"Incorrectly specified the {i}th custom train: missing id")
                return False, config
            if "members" not in train and "member_types" not in train:
                logging.error(f"Incorrectly specified the {i}th custom train: missing members or member_types")
                return False, config
            if "members" in train:
                member_type_check = set()
                for u in train["members"]:
                    if u not in train_units_check:
                        logging.error(f"Train {train['id']} has member {u} that is not defined or already used in a different train composition")
                        return False, config
                    member_type_check.add(train_units_check[u].split("-")[0])
                    train_units_check.pop(u)
                if len(member_type_check) > 1:
                    logging.warning(f"Train {train['id']} has members from different train unit types: {member_type_check}")
            if "member_types" in train:
                member_type_check = set([mem.split("-")[0] for mem in train["member_types"]])
                if len(member_type_check) > 1:
                    logging.warning(f"Train {train['id']} has members from different train unit types: {member_type_check}")
            if "arrival_track" not in train and "start_at_track" not in train:
                logging.warning(f"No 'arrival_track' or 'start_at_track' defined for train {train['id']}, picking random gateway track part")
            if "departure_track" not in train and "end_at_track" not in train:
                logging.warning(f"No 'departure_track' or 'end_at_track' defined for train {train['id']}, picking random gateway track part")
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
                            if location.trackParts[a].type == TrackPartType.Bumper]
                bumper_b = [location.trackParts[a].id 
                            for a in location.trackParts[track_id].bSide 
                            if location.trackParts[a].type == TrackPartType.Bumper]
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
        
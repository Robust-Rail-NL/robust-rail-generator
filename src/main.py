import os
import json
import logging
import argparse
from scenario import ScenarioGenerator, SolverScenarioGenerator
from random_generator import RandomGenerator
from check_config import *
from check_matching import *

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file", help="Name of configuration file for the scenario generation.", required=True)
parser.add_argument("-p", "--path", help="Path to the folder where the --config file can be found (default is /workspace/scenario-planning-inputs/Location_KleineBinckhorst/configurations/ otherwise specify the --path option).", required=False, default=None)
parser.add_argument("-s", "--scenario-file", help="Optional custom name of created scenario file (will be written to the /scenarios/ folder of the same Location_Name folder in the scenario-planning-inputs, unless a different full path is specified here.", required=False, default=None)
parser.add_argument("-l", "--location-path", help="Path to the folder where the location file mentioned in the config can be found (default location is robust-rail-generator/../scenario-planning-inputs/Location_KleineBinckhorst/location.json), otherwise the location.json of the same Location_Name folder will be used if a path is specified.", required=False, default=None)

### Add logging to the arguments
parser.add_argument("--log-level", default="ERROR", required=False, help="Configure the logging level (e.g., INFO, WARNING, ERROR) default=ERROR.")

def create_scenario_from_config(config_file, path=None, scenario_file=None, location_path=None):
    # Use the path if specified, otherwise check at default location for configuration file
    if ".json" not in config_file:
        config_file += ".json"
    if path is None:
        filepath = os.path.join(os.path.dirname(__file__), "..", "..", "scenario-planning-inputs", "Location_KleineBinckhorst", "configurations", config_file)
    elif path == ".":
        filepath = os.path.join(os.getcwd(), config_file)
    else:
        filepath = os.path.join(path, "configurations", config_file)
        location_path = os.path.join(path, "location.json")
        scenario_path = os.path.join(path, "scenarios")
    config = json.load(open(filepath, "r"))

    # Use the location path if specified, otherwise check default location for location file
    if location_path is None:
        location_path = os.path.join(os.path.dirname(__file__), "..", "..", "scenario-planning-inputs", "Location_KleineBinckhorst", "location.json")
    print("location path:", location_path)
    print("config file:", filepath)
    print("scenario file:", scenario_file)

    # Check the configuration file
    correct_file, config = check_configuration_file(config, location_path)
    if not correct_file:
        exit()

    scenario_generator = ScenarioGenerator()
    scenario_generator.load_location(config["location_file"])
    config["track_id_map"] = {tr.id: tr for tr in scenario_generator.location.trackParts}
    scenario_generator.add_start_and_end_times(config["start_time"], config["end_time"])
    # Check the format of the trains
    if config['trains_given']:
        correct_file, config = check_train_details_file(config, scenario_generator.location)
        if not correct_file:
            exit()
    gateways = {"departure": [], "arrival": []}
    if "gateway" in config:
        logging.info("Using specified gateways...")
        result, gateways = check_gateways(config, scenario_generator.location, gateways)
        if not result:
            exit()

    # Setup random generator with seed
    if "seed" not in config:
        config["seed"] = 42
    random_generator = RandomGenerator(scenario_generator, config, scenario_generator.location, gateways)

    # Load the default train materials if specified
    if config["use_default_material"]:
        scenario_generator.add_DefaultTrainUnitTypes()
        random_generator.train_unit_types = scenario_generator.scenario_TrainUnitTypes.copy()
        random_generator.train_units_subtypes = {u.displayName.split("-")[0]: [sub.displayName for sub in random_generator.train_unit_types if u.displayName.split("-")[0] in sub.displayName] for u in random_generator.train_unit_types}
    else:
        random_generator.generate_train_unit_types(config["number_of_train_unit_types"])
        random_generator.train_units_subtypes = {u.displayName.split("-")[0]: [sub.displayName for sub in random_generator.train_unit_types if u.displayName.split("-")[0] in sub.displayName] for u in random_generator.train_unit_types}

    # Add the servicing tasks tasks if specified
    services = {}
    if config["perform_servicing"]:
        for service in config["custom_servicing_tasks"]:
            task_type = scenario_generator.create_TaskType(None, service["type"])
            service_obj = scenario_generator.create_TaskSpec(task_type, service["priority"], service["duration"], service["required_skills"])
            services[service["name"]] = service_obj

    # Add the trains when specified
    if config["trains_given"]:
        create_trains(scenario_generator, config, services)
        matching_possible = check_matching(scenario_generator, config["use_default_material"], config["min_time_in_yard"])
        if not matching_possible:
            logging.error("The specified incoming and outgoing trains do not match. Please check the configuration file.")
            exit()
    else:
        # Generate random trains if none are specified
        random_generator.generate_train_compositions(config, scenario_generator)
        # Check matching of incoming and outgoing trains
        matching_possible = check_matching(scenario_generator, config["use_default_material"], config["min_time_in_yard"])
        while not matching_possible:
            logging.warning("The generated incoming and outgoing trains do not match. Regenerating train compositions.")
            random_generator.reset()
            random_generator.generate_train_compositions(config, scenario_generator)
            matching_possible = check_matching(scenario_generator, config["use_default_material"], config["min_time_in_yard"])
    
    # Also generate the format of the solver
    scenario_generator.create_solver_format_scenario()
    solver_scenario_generator = SolverScenarioGenerator(scenario_generator)
    
    if scenario_file is None:
        # If no name is given, generate it
        num_trains = len(config["custom_trains"]) if config["trains_given"] else config["number_of_trains"]
        custom = f"custom" if config["trains_given"] else f"random_{config['seed']}s"
        scenario_file = f"scenario_{config['location']}_{num_trains}t_{custom}_{config_file.split('/')[-1].split('_')[-1].split('.')[0]}"
    if "/" in scenario_file:
        # Use the specified output path
        output_filepath = scenario_file
    else:
        if path is None:
            scenario_path = os.path.join(os.path.dirname(__file__), "..", "..", "scenario-planning-inputs", "Location_KleineBinckhorst", "scenarios")
        if ".json" not in scenario_file:
            scenario_file += ".json"
        output_filepath = os.path.join(scenario_path,  scenario_file)
    output_solver_filepath = "/".join(output_filepath.split("/")[:-1] + [output_filepath.split("/")[-1].replace("scenario", "scenario_solver")])
    # Write TORS scenario file
    scenario_generator.save_scenario_json(output_filepath)
    # Write Solver format scenario file
    solver_scenario_generator.save_scenario_json(output_solver_filepath)
    print(f"Scenario file created: {output_filepath}")
    print(f"Solver format scenario file created: {output_solver_filepath}")

def create_trains(scenario_generator, config, services):
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
            unmatched_train_units = [scenario_generator.create_TrainUnitUnmatchedMembers(train_unit) for train_unit in train["member_types"]]
            scenario_generator.add_outStandingTrain(
                scenario_generator.create_Train(
                    id=train["id"], 
                    time=0,
                    members=unmatched_train_units, 
                    trackPart=train["end_at_track"],
                    sideTrackPart=train["end_at_track_side"],
                    standingIndex=train["parking_index"] if "parking_index" in train else 1
                )
            )     

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    create_scenario_from_config(args.config_file, args.path, args.scenario_file, args.location_path)

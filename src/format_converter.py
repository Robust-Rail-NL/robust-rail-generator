import sys
import os
import json
import argparse
import logging
from google.protobuf.json_format import ParseDict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "py_protobuf")))
import Location_pb2
from scenario import ScenarioGenerator, SolverScenarioGenerator


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scenario-path", help="Path to scenario file that needs to be converted.", required=False, default=None)
parser.add_argument("-l", "--location-path", help="Path to location file that needs to be converted.", required=False, default=None)
parser.add_argument("--log-level", default="ERROR", required=False, help="Configure the logging level (e.g., INFO, WARNING, ERROR) default=ERROR.")

def convert_location_to_solver(location_file_path):
    """Helper program to convert location files to the robust-rail-solver format scenario."""
    scenario_generator = ScenarioGenerator()
    with open(location_file_path, "r") as f:
        json_location = json.load(f)
    scenario_generator.location = ParseDict(json_location, Location_pb2.Location())
    scenario_generator.convert_location_to_solver_format(location_file_path.replace(".json", "_solver.json"))
    print("Wrote location in solver format to:", location_file_path)

def convert_scenario_from_solver(scenario_file_path):
    """Helper program to convert scenario files to robust-rail-solver format scenario."""
    scenario_generator = ScenarioGenerator()
    scenario_generator.load_scenario(scenario_file_path)
    scenario_generator.create_solver_format_scenario(use_scenario=True)
    solver_scenario_generator = SolverScenarioGenerator(scenario_generator)
    solver_filepath = os.sep.join(scenario_file_path.split(os.sep)[:-1] + [scenario_file_path.split(os.sep)[-1].replace("scenario", "scenario_solver")])
    solver_scenario_generator.save_scenario_json(solver_filepath)
    print("Wrote scenario in solver format to:", solver_filepath)

def example():
    location_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "locations", "simple_service_location.json")
    scenario_filepath_evaluator_format = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "generated_scenarios", "scenario_kleineBinckhorst_6t_custom_config3.json")
    convert_location_to_solver(location_file_path)
    convert_scenario_from_solver(scenario_filepath_evaluator_format)
    # TODO converters from solver to evaluator format


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    if args.location_path:
        convert_location_to_solver(args.location_path)
    if args.scenario_path:
        convert_scenario_from_solver(args.scenario_path)
    
    
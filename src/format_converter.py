import sys
import os
import json
import argparse
import logging

from google.protobuf.json_format import ParseDict

from __init__ import DATA_DIR
from py_protobuf import Location_pb2
from scenario import ScenarioGenerator, SolverScenarioGenerator


parser = argparse.ArgumentParser()
parser.add_argument("-es", "--evaluator-scenario-path", help="Path to evaluator scenario file that needs to be converted to solver format.", required=False, default=None)
parser.add_argument("-sp", "--solver-scenario-path", help="Path to solver scenario file that needs to be converted to evaluator format.", required=False, default=None)
parser.add_argument("-el", "--evaluator-location-path", help="Path to evaluator location file that needs to be converted to solver format.", required=False, default=None)
parser.add_argument("-sl", "--solver-location-path", help="Path to solver location file that needs to be converted to evaluator format.", required=False, default=None)
parser.add_argument("--log-level", default="ERROR", required=False, help="Configure the logging level (e.g., INFO, WARNING, ERROR) default=ERROR.")

def convert_location_to_solver_format(location_file_path):
    """Helper program to convert location files to the robust-rail-solver format scenario."""
    scenario_generator = ScenarioGenerator()
    with open(location_file_path, "r") as f:
        json_location = json.load(f)
    scenario_generator.location = ParseDict(json_location, Location_pb2.Location())
    new_location = location_file_path.replace(".json", "_solver.json")
    scenario_generator.convert_location_to_solver_format(new_location)
    print("[SUCCESS] Wrote location in solver format to:", new_location)

def convert_scenario_to_solver_format(scenario_file_path):
    """Helper program to convert scenario files to robust-rail-solver format scenario."""
    scenario_generator = ScenarioGenerator()
    scenario_generator.load_scenario(scenario_file_path)
    scenario_generator.create_solver_format_scenario(use_scenario=True)
    solver_scenario_generator = SolverScenarioGenerator(scenario_generator)
    solver_filepath = os.sep.join(scenario_file_path.split(os.sep)[:-1] + [scenario_file_path.split(os.sep)[-1].replace("scenario", "scenario_solver")])
    solver_scenario_generator.save_scenario_json(solver_filepath)
    print("[SUCCESS] Wrote scenario in solver format to:", solver_filepath)

def convert_scenario_to_evaluator_format(scenario_file_path):
    """Helper program to convert scenario files to robust-rail-evaluator format scenario."""
    evaluator_scenario_generator = ScenarioGenerator()
    scenario_generator = SolverScenarioGenerator(evaluator_scenario_generator)
    scenario_generator.load_scenario(scenario_file_path)
    scenario_generator.create_evaluator_format_scenario()
    if "_solver" in os.path.basename(scenario_file_path):
        evaluator_filepath = os.path.join(os.path.dirname(scenario_file_path), os.path.basename(scenario_file_path).replace("_solver", ""))
    else:
        evaluator_filepath = os.path.join(os.path.dirname(scenario_file_path), os.path.basename(scenario_file_path).replace(".json", "_evaluator.json"))
    scenario_generator.save_scenario_json(evaluator_filepath)
    print("[SUCCESS] Wrote scenario in solver format to:", evaluator_filepath)

def example():
    location_file_path = os.path.join(DATA_DIR, "example_location.json")
    scenario_filepath_evaluator_format = os.path.join(DATA_DIR, "example_scenario.json")
    convert_location_to_solver_format(location_file_path)
    convert_scenario_to_solver_format(scenario_filepath_evaluator_format)
    # TODO converters from solver to evaluator format


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    if args.evaluator_location_path:
        convert_location_to_solver_format(args.evaluator_location_path)
    if args.evaluator_scenario_path:
        convert_scenario_to_solver_format(args.evaluator_scenario_path)
    if args.solver_scenario_path:
        convert_scenario_to_evaluator_format(args.solver_scenario_path)
    
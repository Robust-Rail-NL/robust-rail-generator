import sys
import os
import json
import logging
from google.protobuf.json_format import ParseDict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "py_protobuf")))
import Location_pb2
import Scenario_pb2
from scenario import ScenarioGenerator, ScenarioGeneratorHIP


def load_location(scenario_generator, file_name):
    logging.info("Call load_location() with", file_name)
    with open(file_name, "r") as f:
        json_location = json.load(f)
    scenario_generator.location = ParseDict(json_location, Location_pb2.Location())


def main(location_file_path, scenario_filepath_evaluator_format, scenario_filepath_solver_format):
    """Helper program to convert easily scenario files to robust-rail-solver (HIP) format scenario"""
    scenario_generator = ScenarioGenerator()
    load_location(scenario_generator, location_file_path)

    scenario_generator.load_scenario(scenario_filepath_evaluator_format)
    scenario_generator.create_HIP_scenario(use_scenario=False)
    
    scenario_generator_hip = ScenarioGeneratorHIP(scenario_generator)
    scenario_generator_hip.save_scenario_json(scenario_filepath_solver_format)
    
    
if __name__ == "__main__":
    # Example files
    location_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "locations", "kleineBinckhorst.json")
    scenario_filepath_formatE = os.path.join(os.path.dirname(__file__), "..", "data", "scenarios", "scenario_kleineBinckhorst_6t_custom_config3.json")
    scenario_filepath_formatS = os.path.join(os.path.dirname(__file__), "..", "data", "scenarios", "scenario_kleineBinckhorst_6t_custom_config3_hip.json")
    main(location_file_path, scenario_filepath_formatE, scenario_filepath_formatS)
    
    
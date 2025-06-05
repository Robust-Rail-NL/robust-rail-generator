import sys
import os
from google.protobuf.json_format import MessageToJson
import json
from google.protobuf.json_format import ParseDict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../py_protobuf")))
import Location_pb2
import Scenario_pb2

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scenario_generator import ScenarioGenerator, ScenarioGeneratorHIP


def load_location(scenario_generator, file_name):
        print("LOG: | call load_location()|")
        with open(file_name, "r") as f:
            json_location = json.load(f)

        print(json_location)
        scenario_generator.location = ParseDict(json_location, Location_pb2.Location())


# Helper program to convert easily scenario files to robust-rail-solver (HIP) format scenario
def main():
    scenario_generator = ScenarioGenerator()
    load_location(scenario_generator, "../../data/scenarios/in_out_standing_test/location.json")

    scenario_generator.load_scenario("../../data/scenarios/in_out_standing_test/scenario.json")
    
    # scenario_generator.convert_location_to_hip_location("./kleineBinckhorst/location_kleineBinckhorst_HIP.json")
    
    scenario_generator.create_HIP_scenario_from_Source()
    
    # scenario_generator.convert_location_to_hip_location("../../data/locations/location_kleineBinckhorst_solver.json")
    scenario_generator_hip = ScenarioGeneratorHIP(scenario_generator)
    
    scenario_generator_hip.save_scenario_json("../../data/scenarios/in_out_standing_test/converted_scenario.json")
    
    
if __name__ == "__main__":
    main()
    
    
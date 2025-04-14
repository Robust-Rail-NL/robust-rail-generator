import sys
import os
from google.protobuf.json_format import MessageToJson

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scenario_generator.scenario_generator import ScenarioGenerator, ScenarioGeneratorHIP


def main():
    scenario_generator = ScenarioGenerator()
    # Create a Combine action type
    task_type = scenario_generator.create_TaskType(None, "inwendige_reiniging")
    #Convert to JSON and print 
    print(MessageToJson(task_type, including_default_value_fields=True))
    # Create a Task Specification, A task specification specifies a certain task
    task_spec = scenario_generator.create_TaskSpec(task_type, 0, 900, ["inwendige_reiniging"])
    print(MessageToJson(task_spec, including_default_value_fields=True))
    # Create a train unit
    trainUnit = scenario_generator.create_TrainUnit("2401", "SLT-4", [task_spec])
    print(MessageToJson(trainUnit, including_default_value_fields=True))
     # Create another train unit
    trainUnit_2 = scenario_generator.create_TrainUnit("2601", "SLT-6", [task_spec])
    print(MessageToJson(trainUnit, including_default_value_fields=True))
    # Create a Train (incoming)
    train = scenario_generator.create_Train(sideTrackPart=42, trackPart=15, time=57600, id="2000", members=[trainUnit])
    print(MessageToJson(train, including_default_value_fields=True))
     # Create another Train (incoming)
    train_2 = scenario_generator.create_Train(sideTrackPart=42, trackPart=15, time=39540, id="3000", members=[trainUnit_2])
    print(MessageToJson(train, including_default_value_fields=True))

    # Create a NonServiceTraffic
    nontraffic_service = scenario_generator.create_NonServiceTraffic([1,2], 9000, 1900, "2000")
    print(MessageToJson(nontraffic_service, including_default_value_fields=True))
    
    # Create DisabledTrackPart
    disabledTrackPart = scenario_generator.create_DisabledTrackPart()
    print(MessageToJson(disabledTrackPart, including_default_value_fields=True))
    
    # Create a single time interval
    time_interval = scenario_generator.create_TimeInterval()
    print(MessageToJson(time_interval, including_default_value_fields=True))
    
    member_staff = scenario_generator.create_MemberOfStaff()
    print(MessageToJson(member_staff, including_default_value_fields=True))
    
    trainUnitType = scenario_generator.create_TrainUnitType( displayName = "SLT-4", carriages = 4, length = 70, combineDuration = 180, splitDuration = 120, backNormTime = 120, backAdditionTime = 18, travelSpeed = 0, startUpTime = 0, typePrefix = "SLT", needsLoco = False, isLoco = False, needsElectricity = True, idPrefix = None)
    print(MessageToJson(trainUnitType, including_default_value_fields=True))
    
    trainUnitType_2 = scenario_generator.create_TrainUnitType( displayName = "SLT-6", carriages = 6, length = 101, combineDuration = 180, splitDuration = 120, backNormTime = 120, backAdditionTime = 18, travelSpeed = 0, startUpTime = 0, typePrefix = "SLT", needsLoco = False, isLoco = False, needsElectricity = True, idPrefix = None)
    print(MessageToJson(trainUnitType_2, including_default_value_fields=True))
    # Add incoming train 
    scenario_generator.add_incomingTrain(train)
    # Add another incoming train 
    scenario_generator.add_incomingTrain(train_2)
    # Show incoming trains
    in_trains = getattr(scenario_generator.scenario, "in")
    for train_ in in_trains:
        print(MessageToJson(train_, including_default_value_fields=True))
    
    
    # Create an outgoing train and its members and tasks
    trainUnit_out = scenario_generator.create_TrainUnit("****", "SLT-4", [])
    trainUnit_out_2 = scenario_generator.create_TrainUnit("****", "SLT-6", [])
    
    train_out = scenario_generator.create_Train(sideTrackPart=42, trackPart=15, time=106020, id="2606", members=[trainUnit_out])
    train_out_2 = scenario_generator.create_Train(sideTrackPart=42, trackPart=15, time=106020, id="2406", members=[trainUnit_out_2])
    
    scenario_generator.add_outgoingTrain(train_out)
    scenario_generator.add_outgoingTrain(train_out_2)
    
    out_trains = scenario_generator.scenario.out
    for train_ in out_trains:
        print(MessageToJson(train_, including_default_value_fields=True))
    
    
    # Add start and end time of the scenario
    scenario_generator.add_start_and_end_times(36240, 106020)
    
    # Add train unit type to the scenario
    scenario_generator.add_TrainUnitType(trainUnitType)
    scenario_generator.add_TrainUnitType(trainUnitType_2)
    
    
    # print(MessageToJson(train_out, including_default_value_fields=True))
    
    # Show scenario
    print(MessageToJson(scenario_generator.scenario, including_default_value_fields=True))
    
    scenario_generator.save_scenario_json("scenario.json")
    # Create HIP based scenario from the standard 
    
    scenario_generator_hip = ScenarioGeneratorHIP(scenario_generator)
    scenario_generator.create_HIP_scenario()
        
    
    scenario_generator_hip.save_scenario_json("scenario_hip.json")
    
    # scenario_generator.load_location("../../../data/locations/location_heerlen.json")
    
    scenario_generator.load_location("../../../data/locations/location_kleineBinckhorst.json")
    
    scenario_generator.convert_location_to_hip_location("HIP_compatible_location.json")

if __name__ == "__main__":
    main()
import sys
import os
from google.protobuf.json_format import MessageToJson

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scenario_generator.scenario_generator import ScenarioGenerator, ScenarioGeneratorHIP


def main():
    scenario_generator = ScenarioGenerator()
    # Add the standard Dutch train types
    scenario_generator.add_DefaultTrainUnitTypes()

    # Altered file with no station platforms for conformity and servicing platforms at track t407 and 404
    scenario_generator.load_location("location_enkhuizen_test_no_platforms")

    task_type = scenario_generator.create_TaskType(None, "inwendige_reiniging")
    task_spec = scenario_generator.create_TaskSpec(task_type, 0, 900, ["inwendige_reiniging"])

 
    trainUnit_1 = scenario_generator.create_TrainUnit("2401", "SLT-4", [task_spec])
    trainUnit_2 = scenario_generator.create_TrainUnit("2601", "SLT-6", [task_spec])
    trainUnit_3 = scenario_generator.create_TrainUnit("2801", "SNG-3", [])
    trainUnit_4 = scenario_generator.create_TrainUnit("2802", "SNG-4", [])

    # Train 1 starts at track tEH (incoming track), visits track t401 (station platform), and should be serviced and parked (both at t404)
    train_1 = scenario_generator.create_Train(sideTrackPart=21, trackPart=1, standingIndex=4, time=600, id="2000", members=[trainUnit_1])
    # Train 2 starts at track tEH (incoming track), should visit track t402 (station platform) and should be serviced and parked (both at t407)
    train_2 = scenario_generator.create_Train(sideTrackPart=21, trackPart=2, standingIndex=7, time=900, id="3000", members=[trainUnit_2])
    # Train 3a starts at track t405 (parking track), should visit track t402 (station, after train2), be combined with 3b and depart (leave the scenario at tEH)
    train_3a = scenario_generator.create_Train(sideTrackPart=5, trackPart=2, canDepartFromAnyTrack=False, time=1200, id="4001", members=[trainUnit_3])
    # Train 3b starts at track t406 (parking track), should visit track t402 (station, after train2), be combined with 3a and depart (leave the scenario at tEH)
    train_3b = scenario_generator.create_Train(sideTrackPart=6, trackPart=2, canDepartFromAnyTrack=False, time=1300, id="4002", members=[trainUnit_4])
    train_3 = scenario_generator.create_Train(sideTrackPart=1, trackPart=21, canDepartFromAnyTrack=False, time=1500, id="4000", members=[trainUnit_4, trainUnit_3])

    
    # Create a single time interval
    time_interval = scenario_generator.create_TimeInterval(0, 7200)    
    member_staff = scenario_generator.create_MemberOfStaff()

    scenario_generator.add_inStandingTrain(train_1)
    scenario_generator.add_outStandingTrain(train_1)
    scenario_generator.add_incomingTrain(train_2)  
    scenario_generator.add_outStandingTrain(train_2)  
    scenario_generator.add_inStandingTrain(train_3a)
    scenario_generator.add_inStandingTrain(train_3b)
    scenario_generator.add_outgoingTrain(train_3)
        
    scenario_generator.add_start_and_end_times(0, 3600)
    print(MessageToJson(scenario_generator.scenario, including_default_value_fields=True))
    
    # Create HIP based scenario from the standard scenario
    scenario_generator.create_HIP_scenario()
    scenario_generator.save_scenario_json(os.path.join(os.path.dirname(__file__), "scenario_file.json"))
    
    scenario_generator_hip = ScenarioGeneratorHIP(scenario_generator)
    scenario_generator_hip.save_scenario_json("scenario_hip.json")
    
if __name__ == "__main__":
    main()
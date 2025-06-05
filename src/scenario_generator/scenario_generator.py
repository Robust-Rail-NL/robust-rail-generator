import sys
import os
import json
from typing import List, Dict, Any

from typing import Union
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import ParseDict


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../py_protobuf")))

# Import standard protos (Scenario, Location, TrainUintTypes, Utilities)
import Scenario_pb2
import TrainUnitTypes_pb2
import Location_pb2
import Utilities_pb2

# Import HIP required protos
import Scenario_HIP_pb2
import Location_HIP_pb2


# To better understand the structure and the parameters/arguments please refer to the Scenario.proto 

class ScenarioGenerator:
    def __init__(self):
        """Initialize the scenario generator"""
      
        print("LOG: | Scenario Generator has been initialized. |")
        self.scenario = Scenario_pb2.Scenario()
        self.scenario_in: List[Scenario_pb2.Train] = []
        self.scenario_out: List[Scenario_pb2.Train] = []

        self.scenario_TrainUnitTypes: List[TrainUnitTypes_pb2.TrainUnitType] = []
        self.scenario_hip =  Scenario_HIP_pb2.Scenario()
        
        # Location where the scenario happens
        self.location = Location_pb2.Location()
        self.location_hip = Location_HIP_pb2.Location()
    
    # Converts protobuf object into json representation and saves it into .json file 
    def save_scenario_json(self, file_name: str):
        print("LOG: | call save_scenario_json()|")
        json_data = MessageToJson(self.scenario, including_default_value_fields=True, indent=4)
        with open(file_name, "w") as f:
            f.write(json_data)
            
    def load_scenario(self, file_name):
        print("LOG: | call load_scenario()|")
        with open(file_name, "r") as f:
            json_scenario = json.load(f)
        self.scenario = ParseDict(json_scenario, Scenario_pb2.Scenario())
        
    
    def create_HIP_scenario(self):
        print("LOG: | call create_HIP_scenario()|")
        incomingTrains = getattr(self.scenario_hip, "in")
        for train_standard in self.scenario_in:
            train = incomingTrains.trains.add()
            train.entryTrackPart = train_standard.sideTrackPart
            train.firstParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.id = train_standard.id
            
            members_standard = train_standard.members
            for member in members_standard:
                train_member = train.members.add()
                train_member.trainUnit.id = member.id
                
                for task_standard in member.tasks:
                    task = train_member.tasks.add()
                    if task_standard.type.predefined:
                        task.type.predefined = task_standard.type.predefined
                    elif task_standard.type.other:
                        task.type.other = task_standard.type.other
                    
                    task.priority = task_standard.priority
                    task.duration = task_standard.duration
                
                #Get typeDisplayName associated to the typeDisplayName
                for trainUnitType in self.scenario_TrainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_member.trainUnit.type.displayName = trainUnitType.typePrefix          
                        train_member.trainUnit.type.carriages = trainUnitType.carriages
                        train_member.trainUnit.type.length = trainUnitType.length
                        train_member.trainUnit.type.combineDuration = trainUnitType.combineDuration
                        train_member.trainUnit.type.splitDuration = trainUnitType.splitDuration
                        train_member.trainUnit.type.backNormTime = trainUnitType.backNormTime
                        train_member.trainUnit.type.backAdditionTime = trainUnitType.backAdditionTime
        
       
        trainRequest = getattr(self.scenario_hip, "out")
        for train_standard in self.scenario_out:
            train = trainRequest.trainRequests.add()
            train.leaveTrackPart = train_standard.sideTrackPart
            train.lastParkingTrackPart = train_standard.parkingTrackPart
            
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.displayName = train_standard.id
            
            ## Add train units 
            
            
            members_standard = train_standard.members
            for member in members_standard:
                train_unit = train.trainUnits.add()
                # train_unit.id = member.id -> it is "***" in cTORS in HIP it is simply undefined
                 
                for trainUnitType in self.scenario_TrainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_unit.type.displayName = trainUnitType.typePrefix          
                        train_unit.type.carriages = trainUnitType.carriages
                        train_unit.type.length = trainUnitType.length
                        train_unit.type.combineDuration = trainUnitType.combineDuration
                        train_unit.type.splitDuration = trainUnitType.splitDuration
                        train_unit.type.backNormTime = trainUnitType.backNormTime
                        train_unit.type.backAdditionTime = trainUnitType.backAdditionTime
                
        inStandningTrains = getattr(self.scenario_hip, "inStanding")
        
        _inStandingTrains = getattr(self.scenario, "inStanding")
        
        for train_standard in _inStandingTrains:
            train = inStandningTrains.trains.add()
            train.entryTrackPart = train_standard.sideTrackPart
            train.firstParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.id = train_standard.id
            
            members_standard = train_standard.members
            for member in members_standard:
                train_member = train.members.add()
                train_member.trainUnit.id = member.id
                
                for task_standard in member.tasks:
                    task = train_member.tasks.add()
                    if task_standard.type.predefined:
                        task.type.predefined = task_standard.type.predefined
                    elif task_standard.type.other:
                        task.type.other = task_standard.type.other
                   
                    task.priority = task_standard.priority
                    task.duration = task_standard.duration
                
                #Get typeDisplayName associated to the typeDisplayName
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_member.trainUnit.type.displayName = trainUnitType.typePrefix          
                        train_member.trainUnit.type.carriages = trainUnitType.carriages
                        train_member.trainUnit.type.length = trainUnitType.length
                        train_member.trainUnit.type.combineDuration = trainUnitType.combineDuration
                        train_member.trainUnit.type.splitDuration = trainUnitType.splitDuration
                        train_member.trainUnit.type.backNormTime = trainUnitType.backNormTime
                        train_member.trainUnit.type.backAdditionTime = trainUnitType.backAdditionTime
                        
        trainRequest = getattr(self.scenario_hip, "outStanding")
                
        for train_standard in self.scenario.outStanding:
            train = trainRequest.trainRequests.add()
            train.leaveTrackPart = train_standard.sideTrackPart
            train.lastParkingTrackPart = train_standard.parkingTrackPart
            
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.displayName = train_standard.id
            
            ## Add train units 
            
            
            members_standard = train_standard.members
            for member in members_standard:                
                train_unit = train.trainUnits.add()
                # train_unit.id = member.id -> it is "***" in cTORS in HIP it is simply undefined
                 
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_unit.type.displayName = trainUnitType.typePrefix          
                        train_unit.type.carriages = trainUnitType.carriages
                        train_unit.type.length = trainUnitType.length
                        train_unit.type.combineDuration = trainUnitType.combineDuration
                        train_unit.type.splitDuration = trainUnitType.splitDuration
                        train_unit.type.backNormTime = trainUnitType.backNormTime
                        train_unit.type.backAdditionTime = trainUnitType.backAdditionTimes               

        # print(MessageToJson(self.scenario_hip, including_default_value_fields=True))
        
       
    def create_HIP_scenario_from_Source(self):
        print("LOG: | call create_HIP_scenario()|")
        incomingTrains = getattr(self.scenario_hip, "in")
        
        self.scenario_hip.startTime = self.scenario.startTime
        self.scenario_hip.endTime = self.scenario.endTime
        
        
        _in = getattr(self.scenario, "in")
        
        for train_standard in _in:
            train = incomingTrains.trains.add()
            train.entryTrackPart = train_standard.sideTrackPart
            train.firstParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.id = train_standard.id
            
            members_standard = train_standard.members
            for member in members_standard:
                train_member = train.members.add()
                train_member.trainUnit.id = member.id
                
                for task_standard in member.tasks:
                    task = train_member.tasks.add()
                    if task_standard.type.predefined:
                        task.type.predefined = task_standard.type.predefined
                    elif task_standard.type.other:
                        task.type.other = task_standard.type.other
                    
                    task.priority = task_standard.priority
                    task.duration = task_standard.duration
                
                #Get typeDisplayName associated to the typeDisplayName
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_member.trainUnit.type.displayName = trainUnitType.typePrefix          
                        train_member.trainUnit.type.carriages = trainUnitType.carriages
                        train_member.trainUnit.type.length = trainUnitType.length
                        train_member.trainUnit.type.combineDuration = trainUnitType.combineDuration
                        train_member.trainUnit.type.splitDuration = trainUnitType.splitDuration
                        train_member.trainUnit.type.backNormTime = trainUnitType.backNormTime
                        train_member.trainUnit.type.backAdditionTime = trainUnitType.backAdditionTime
                       
        
        
        inStandningTrains = getattr(self.scenario_hip, "inStanding")
        
        _inStandingTrains = getattr(self.scenario, "inStanding")
        
        for train_standard in _inStandingTrains:
            train = inStandningTrains.trains.add()
            train.entryTrackPart = train_standard.sideTrackPart
            train.firstParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.id = train_standard.id
            
            members_standard = train_standard.members
            for member in members_standard:
                train_member = train.members.add()
                train_member.trainUnit.id = member.id
                
                for task_standard in member.tasks:
                    task = train_member.tasks.add()
                    if task_standard.type.predefined:
                        task.type.predefined = task_standard.type.predefined
                    elif task_standard.type.other:
                        task.type.other = task_standard.type.other
                   
                    task.priority = task_standard.priority
                    task.duration = task_standard.duration
                
                #Get typeDisplayName associated to the typeDisplayName
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_member.trainUnit.type.displayName = trainUnitType.typePrefix          
                        train_member.trainUnit.type.carriages = trainUnitType.carriages
                        train_member.trainUnit.type.length = trainUnitType.length
                        train_member.trainUnit.type.combineDuration = trainUnitType.combineDuration
                        train_member.trainUnit.type.splitDuration = trainUnitType.splitDuration
                        train_member.trainUnit.type.backNormTime = trainUnitType.backNormTime
                        train_member.trainUnit.type.backAdditionTime = trainUnitType.backAdditionTime
                        
            
        trainRequest = getattr(self.scenario_hip, "out")
        _out = getattr(self.scenario, "out")
        
        for train_standard in _out:
            train = trainRequest.trainRequests.add()
            train.leaveTrackPart = train_standard.sideTrackPart
            train.lastParkingTrackPart = train_standard.parkingTrackPart
            
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.displayName = train_standard.id
            
            ## Add train units 
            
            
            members_standard = train_standard.members
            for member in members_standard:                
                train_unit = train.trainUnits.add()
                # train_unit.id = member.id -> it is "***" in cTORS in HIP it is simply undefined
                 
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_unit.type.displayName = trainUnitType.typePrefix          
                        train_unit.type.carriages = trainUnitType.carriages
                        train_unit.type.length = trainUnitType.length
                        train_unit.type.combineDuration = trainUnitType.combineDuration
                        train_unit.type.splitDuration = trainUnitType.splitDuration
                        train_unit.type.backNormTime = trainUnitType.backNormTime
                        train_unit.type.backAdditionTime = trainUnitType.backAdditionTime
        
       
        trainRequest = getattr(self.scenario_hip, "outStanding")
                
        for train_standard in self.scenario.outStanding:
            train = trainRequest.trainRequests.add()
            train.leaveTrackPart = train_standard.sideTrackPart
            train.lastParkingTrackPart = train_standard.parkingTrackPart
            
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.displayName = train_standard.id
            
            ## Add train units 
            
            
            members_standard = train_standard.members
            for member in members_standard:                
                train_unit = train.trainUnits.add()
                # train_unit.id = member.id -> it is "***" in cTORS in HIP it is simply undefined
                 
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_unit.type.displayName = trainUnitType.typePrefix          
                        train_unit.type.carriages = trainUnitType.carriages
                        train_unit.type.length = trainUnitType.length
                        train_unit.type.combineDuration = trainUnitType.combineDuration
                        train_unit.type.splitDuration = trainUnitType.splitDuration
                        train_unit.type.backNormTime = trainUnitType.backNormTime
                        train_unit.type.backAdditionTime = trainUnitType.backAdditionTime
                
        print(MessageToJson(self.scenario_hip, including_default_value_fields=True))
        
    # Add outgoing train to the scenario
    def add_outgoingTrain(self, out_train: Scenario_pb2.Train):
        print("LOG: | call add_outgoingTrain()|")
        
        trainUnits = out_train.members
        for trainUnit in trainUnits:
            trainUnit.id = "****"
        
        train = self.scenario.out.add()
        train.MergeFrom(out_train)
        
        self.scenario_out.append(out_train)
    
    # Add incoming Train to the scenario
    def add_incomingTrain(self, in_train: Scenario_pb2.Train):
        print("LOG: | call add_incomingTrain()|")
        train = getattr(self.scenario, "in").add()
        train.MergeFrom(in_train)
        
        self.scenario_in.append(in_train)
        
        # train.sideTrackPart = in_train.sideTrackPart
        # train.parkingTrackPart = in_train.parkingTrackPart
        # train.time = in_train.time
        # train.id = in_train.id
        
        # train.members.MergeFrom(in_train.members)
        
        
        # train.canDepartFromAnyTrack = in_train.canDepartFromAnyTrack
        # train.standingIndex = in_train.standingIndex
        # train.minimumDuration = in_train.minimumDuration
        
    # Add inStanding Train to the scenario
    def add_inStandingTrain(self, in_standingTrain: Scenario_pb2.Train):
        print("LOG: | call add_inStandingTrain()|")
        train = self.scenario.inStanding.add()
        train.MergeFrom(in_standingTrain)
        
    # Add outStanding Train to the scenario
    def add_outStandingTrain(self, out_standingTrain: Scenario_pb2.Train):
        print("LOG: | call add_outStandingTrain()|")
        trainUnits = out_standingTrain.members
        for trainUnit in trainUnits:
            trainUnit.id = "****"
        
        train = self.scenario.outStanding.add()
        train.MergeFrom(out_standingTrain)
        
    # Add nonServiceTraffic to the scenario
    def add_nonServiceTraffic(self, nonServiceTraffic: Scenario_pb2.NonServiceTraffic):
        print("LOG: | call add_nonServiceTraffic()|")
        service = self.scenario.nonServiceTraffic.add()
        service.MergeFrom(nonServiceTraffic)
        
     # Add disabledTrackPart to the scenario
    def add_disabledTrackPart(self, disabledTrackPart: Scenario_pb2.DisabledTrackPart):
        print("LOG: | call add_disabledTrackPart()|")
        track_part = self.scenario.disabledTrackPart.add()
        track_part.MergeFrom(disabledTrackPart)
        
    # Add MemberOfStaff to the scenario
    def add_workers(self, workers: Scenario_pb2.MemberOfStaff):
        print("LOG: | call add_workers()|")
        staff = self.scenario.workers.add()
        staff.MergeFrom(workers)
    
    # Add startTime and endTime to scenario
    def add_start_and_end_times(self, start: int, end: int):
        print("LOG: | call add_start_and_end_times()|")
        self.scenario.startTime = start
        self.scenario.endTime = end
        
    # Add TrainUnitType to scenario    
    def add_TrainUnitType(self, trainUnitType: TrainUnitTypes_pb2.TrainUnitType):
        print("LOG: | call add_TrainUnitType()|")
        trainUnitTypes = self.scenario.trainUnitTypes.add()
        trainUnitTypes.MergeFrom(trainUnitType)
        
        self.scenario_TrainUnitTypes.append(trainUnitType)
        
    # Create a incoming/leaving train or a train which stays on the location 
    def create_Train(self, sideTrackPart: int, trackPart: int, time: int, id: str, members: List[Scenario_pb2.TrainUnit], canDepartFromAnyTrack: bool = None, standingIndex: float = None, minimumDuration: str = None)->Scenario_pb2.Train:
        """_summary_
        Method used to create train objects that are added either as an in- or an out-going train.

        For outgoing train with TrainUnits with only a type and no ID, enter the train unit objects that are created with create_TrainUnitUnmatchedMembers()

        Args:
            trackPart (int): railroad that this train arrives/departs at
            sideTrackPart (int): side of the railroad track part that identifies the end of the track, used to claim space on a track (often a bumper, or the next part connected to the railroad)
            time (int): Arrival/Departure on the track, (and departure from the bumper), times are in seconds since the epoch
            id (str): unique identifier of the Train 
            members (List[Scenario_pb2.TrainUnit]): train units in the train
            canDepartFromAnyTrack (bool): For outstanding trains: set to true to allow departures from any track, instead of just the parkingTrackPart (TORS required, not used)
            standingIndex (float): if train is in- or outstanding and there are multiple trains on one track, use this to determine the index of the train on the track, with lower indices at the A-side of the track
            minimumDuration (str): minimum duration on the track part where the train arrives/departs

        Returns:
            Scenario_pb2.Train: incoming/leaving train or a train which stays on the location 
        """
        print("LOG: | call create_Train() |")
        
        train = Scenario_pb2.Train()
        
        train.sideTrackPart = sideTrackPart 
        train.parkingTrackPart = trackPart
        train.time = time
        train.id = id
        
        # Merge all the members a.k.a TrainUnit(s) with the existing members if there are
        train.members.MergeFrom(members)

        if canDepartFromAnyTrack:
            train.canDepartFromAnyTrack = canDepartFromAnyTrack
        if standingIndex:
            train.standingIndex = standingIndex
        if minimumDuration:
            train.minimumDuration = minimumDuration
        
        return train
    
    # Create a TaskSpec which specifies a certain task, with its type, priority, duration and the 
    # requiredSkills  (no personnel required) e.g.: ["B-controle"] => one member of staff with skill "B-controle" required
    def create_TaskSpec(self, taskType: Location_pb2.TaskType, priority: int, duration: int, requiredSkills: List[str])->Scenario_pb2.TaskSpec:
        """_summary_

        Args:
            taskType (Location_pb2.TaskType): type of the task
            priority (int): lower values indicate that this task is more important, a value of zero indicates that the task is required.
            duration (int): time this task takes, in seconds
            requiredSkills (List[str]): skills required to perform the task. Each entry in the list indicates that a member of staff with the given skill is required.

        Returns:
            Scenario_pb2.TaskSpec: task specification specifies a certain task.
        """
        print("LOG: | call create_TaskSpec() |")
        
        task_spec = Scenario_pb2.TaskSpec()
        
        # Since taskType is a protobuf object its content must be copied to the other proto object
        # indeed it is a nested message structure => TaskSpec contains TaskType message 
        task_spec.type.CopyFrom(taskType)
        
        task_spec.priority = priority
       
        task_spec.duration = duration
        
        task_spec.requiredSkills.MergeFrom(requiredSkills)
    
        return task_spec
        

    #Create a train unit 
    # "id" is the train unit id e.g.: "2401"
    # "typeDisplayName" is the type name e.g.:  "SLT4"
    def create_TrainUnit(self, id: str, typeDisplayName: str, tasks: List[Scenario_pb2.TaskSpec]):
        """_summary_

        Args:
            id (str):  A unique identifier of the unit
            typeDisplayName (str): displayName of the TrainUnitType
            tasks (List[Scenario_pb2.TaskSpec]): Tasks for this train unit

        Returns:
            _type_: represents a combination of carriages which can move independently
        """
        print("LOG: | call create_TrainUnit() |")
        trainUnit = Scenario_pb2.TrainUnit()
        
        trainUnit.id = id
        trainUnit.typeDisplayName = typeDisplayName
        
        trainUnit.tasks.MergeFrom(tasks)
        
        return trainUnit


    # Create a train unit with unmatched members (outgoing train request with unit types)
    # Such a train has an empty id **** and always has an empty task list.
    # "typeDisplayName" is the type name e.g.:  "SLT4"
    def create_TrainUnitUnmatchedMembers(self, typeDisplayName: str):
        print("LOG: | call create_TrainUnitUnmatchedMembers() |")
        trainUnit = Scenario_pb2.TrainUnit()
        
        trainUnit.id = "****"
        trainUnit.typeDisplayName = typeDisplayName
        # trainUnit.tasks = []
        return trainUnit
        

    # Create a task type - which is the task assigned o the give train (in fact a train
    # can contain a list of tasks). e.g., "type" : {"other" : "inwendige_reiniging"} 
    def create_TaskType(self, predefinedTaskType: int = None, other: str = None)->Location_pb2.TaskType:
        """_summary_

        Args:
            predefinedTaskType (int, optional):  If the task type maps to one of PredefinedTaskType, use this type here. Defaults to None.
            other (str, optional): Otherwise, specify a custom name. Defaults to None.

        Raises:
            ValueError: If non of them defined

        Returns:
            Location_pb2.TaskType: Specifies the task type - PredefinedTaskType {Move, Split, Combine, Wait, Arrive, Exit, Walking, Break, NonService, BeginMove, EndMove}
        """
        print("LOG: | call create_TaskType() |")
        task_type = Location_pb2.TaskType()
        
        if predefinedTaskType:
            task_type.predefined = predefinedTaskType
            return task_type
        elif other:
            task_type.other = other
            return task_type
        else:
            raise ValueError("Either 'predefinedTaskType' or 'other' must be provided.")

    # Create a Traffic without service
    def create_NonServiceTraffic(self, members: List[int], arrival: int, departure: int, id: str)->Scenario_pb2.NonServiceTraffic:
        """_summary_

        Args:
            members (List[int]): reserved part of the location send in track parts
            arrival (int): Arrival on the track (Times are in seconds since the epoch)
            departure (int):  departure from the track (Times are in seconds since the epoch)
            id (str): unique identifier

        Returns:
            Scenario_pb2.NonServiceTraffic: Traffic without service
        """
        print("LOG: | call create_NonServiceTraffic() |")
        
        nonServiceTraffic = Scenario_pb2.NonServiceTraffic()
        
        nonServiceTraffic.members.extend(members)
        nonServiceTraffic.arrival = arrival
        nonServiceTraffic.departure = departure
        nonServiceTraffic.id = id
        
        return nonServiceTraffic
    
    # Create and incoming magic train
    def create_DisabledTrackPart(self, trackPart: int = None, arrival: int = None, departure: int = None)->Scenario_pb2.DisabledTrackPart:
        """_summary_

        Args:
            trackPart (int, optional): TrackPart ID of the location this train fetches wizards from, using 9.75 as default doesn't work.. Defaults to None.
            arrival (int, optional):  Arrival on the track. Defaults to None.
            departure (int, optional): departure from the track. Defaults to None.

        Returns:
            Scenario_pb2.DisabledTrackPart: An incoming magic train

        """
        print("LOG: | call create_NonServiceTraffic() |")
        
        disabled_trackpart = Scenario_pb2.DisabledTrackPart()
        if trackPart:
            disabled_trackpart.trackPart = trackPart
        if arrival:
            disabled_trackpart.arrival = arrival
        if departure:
            disabled_trackpart.departure = departure
      
        return disabled_trackpart

    # Create a single time interval
    def create_TimeInterval(self, start: float = None, end: float = None)->Utilities_pb2.TimeInterval:
        """_summary_

        Args:
            start (float, optional):  Start of the interval in seconds since the epoch. Defaults to None.
            end (float, optional): End of the interval in seconds since the epoch. Defaults to None.

        Returns:
            Utilities_pb2.TimeInterval: representing a single time interval.
        """
        print("LOG: | call create_TimeInterval() |")
        timeInterval = Utilities_pb2.TimeInterval()

        if start:
            timeInterval.start = start
        if end:
            timeInterval.end = end
        
        return timeInterval            
     
    # Create Member of Staff which is a human that is able to perform various tasks at the facility
    def create_MemberOfStaff(self, id: int = None, type: str = None, skills: List[str] = None, shifts: List[Utilities_pb2.TimeInterval] = None, breakWindows: List[Utilities_pb2.TimeInterval] = None, breakDuration: float = None, startLocationId: int = None, endLocationId: int = None, canMoveTrains: bool = None, name: str = None, breakLocationId: int = None)->Scenario_pb2.MemberOfStaff:
        """_summary_

        Args:
            id (int, optional): unique ID which is referenced by other messages. Defaults to None.
            type (str, optional): type of staff, e.g. engineer, cleaning team, etc.. Defaults to None.
            skills (List[str], optional): the member of staff possesses. Defaults to None.
            shifts (List[Utilities_pb2.TimeInterval], optional):  intervals during which the member of staff is present. Defaults to None.
            breakWindows (List[Utilities_pb2.TimeInterval], optional): intervals in which breaks must take place. Defaults to None.
            breakDuration (float, optional): duration of the break in seconds. duration of the break in seconds to None.
            startLocationId (int, optional): location (trackpart) of the member of staff at the start of the shift. Defaults to None.
            endLocationId (int, optional): location (trackpart) of the member of staff at the end of the shift. Defaults to None.
            canMoveTrains (bool, optional): Indicates whether the member of staff can move trains. Defaults to None.
            name (str, optional): name of the staff member. Defaults to None.
            breakLocationId (int, optional): location (trackpart) of the member of staff during breaks. Defaults to None.

        Returns:
            Scenario_pb2.MemberOfStaff: a human that is able to perform various tasks at the facility
        """
        print("LOG: | call create_MemberOfStaff() |")
        
        memberOfStuff = Scenario_pb2.MemberOfStaff()
        
        if id:
            memberOfStuff.id = id
        if type:
            memberOfStuff.type = type
        if skills:
            memberOfStuff.skills.extend(skills)
        if shifts:
            memberOfStuff.shifts.MergeFrom(shifts)
        if  breakWindows:
            memberOfStuff.breakWindows.MergeFrom(breakWindows)   
        if breakDuration:
            memberOfStuff.breakDuration = breakDuration
        if startLocationId:
            memberOfStuff.startLocationId = startLocationId
        if endLocationId:
            memberOfStuff.endLocationId = endLocationId
        if canMoveTrains:
            memberOfStuff.canMoveTrains = canMoveTrains
        if name:
            memberOfStuff.name = name
        if breakLocationId:
            memberOfStuff.breakLocationId = breakLocationId
        
        return memberOfStuff
    
    # Create Train Unit type
    def create_TrainUnitType(self, displayName: str, carriages: int, length: float, combineDuration: int, splitDuration: int, backNormTime: int, backAdditionTime: int, travelSpeed: int, startUpTime: int, typePrefix: str, needsLoco: bool, isLoco: bool, needsElectricity: bool, idPrefix: int = None)->TrainUnitTypes_pb2.TrainUnitType:
        """_summary_

        Args:
            displayName (str): Name of the train unit type. For example, "SGM" or "SLT". Currently, this is "SLT4" or "SLT6", see 'typeprefix' later on. #warning
            carriages (int):  This is the total number of carriages, including the first and last carriage.
            length (float):  Length of this train unit, in meters
            combineDuration (int):  Time it takes to perform a combine in seconds
            splitDuration (int): Time it takes to perform a split in seconds
            backNormTime (int):  kopmaaktijd = backNormTime + #carriage * backAdditionTime
            backAdditionTime (int): _description_
            travelSpeed (int):  this is the speed of the train but that is yet to be determined whether that is here or location specific #warning
            startUpTime (int): Startup + Shutdown
            typePrefix (str): for example: "SLT" or "VIRM"
            needsLoco (bool):  This TrainUnitType needs a locomotive, e.g. it cannot drive itself
            isLoco (bool): Can pull/push other wagons
            needsElectricity (bool): / This train needs electricity, so it can only drive on electrified track parts
            idPrefix (int, optional):  Prefix of train IDs of this type (i.e., the last two digits are removed).  For example, for SLT4 this is 24. Defaults to None.

        Returns:
            TrainUnitTypes_pb2.TrainUnitType: _description_
        """
        print("LOG: | call create_TrainUnitType() |")

        trainUnitType = TrainUnitTypes_pb2.TrainUnitType()
        
        trainUnitType.displayName = displayName
        trainUnitType.carriages = carriages
        trainUnitType.length = length
        trainUnitType.combineDuration = combineDuration
        trainUnitType.splitDuration = splitDuration
        trainUnitType.backNormTime = backNormTime
        trainUnitType.backAdditionTime = backAdditionTime
        trainUnitType.travelSpeed = travelSpeed
        trainUnitType.startUpTime = startUpTime
        trainUnitType.typePrefix = typePrefix
        trainUnitType.needsLoco = needsLoco
        trainUnitType.isLoco = isLoco
        trainUnitType.needsElectricity = needsElectricity
        
        if idPrefix:
            trainUnitType.idPrefix = idPrefix
            
        return trainUnitType
    

    # Create a TrainUnit which is an element of the members in the scenario
    #def create_TrainUnit(self, unit_id: str, type_display_name: str, taskSpec: Scenario_pb2.TaskSpec) -> Scenario_pb2.TrainUnit: 
    #   print()
    # def create_Train(self)
    

    # Load json format location  
    def load_location(self, file_name):
        print("LOG: | call load_location()|")
        if not os.path.isfile(file_name):
            file_name = os.path.join(os.path.dirname(__file__), "..", "..", "data", "locations", f"{file_name}{'.json' if '.json' not in file_name else ''}")
        with open(file_name, "r") as f:
            json_location = json.load(f)
        
        self.location = ParseDict(json_location, Location_pb2.Location())

    # Converts a standard location into a HIP compatible location file
    def convert_location_to_hip_location(self, file_name):
        print("LOG: | call convert_location_to_hip_location()|")
        
        # Check if self.location is not empty
        if self.location.ListFields():
            trackParts = self.location.trackParts
            for trackPart in trackParts:
                hip_trackPart = self.location_hip.trackParts.add()
                    
                hip_trackPart.id = trackPart.id
                
                if trackPart.type == Location_pb2.TrackPartType.Building:
                    print("Building type cannot be added to HIP")
                else:
                   hip_trackPart.type = trackPart.type
                
                hip_trackPart.aSide.MergeFrom(trackPart.aSide)
                hip_trackPart.bSide.MergeFrom(trackPart.bSide)
                hip_trackPart.length = trackPart.length
                hip_trackPart.name = trackPart.name
                hip_trackPart.sawMovementAllowed = trackPart.sawMovementAllowed
                hip_trackPart.parkingAllowed = trackPart.parkingAllowed
                
                
            facilities = self.location.facilities
            for facility in facilities:
                hip_facility = self.location_hip.facilities.add()
                hip_facility.id = facility.id  
                hip_facility.type = facility.type
                hip_facility.relatedTrackParts.MergeFrom(facility.relatedTrackParts)
                
                if facility.taskTypes:
                    for facility_taskTypes in facility.taskTypes:
                        hip_facility_taskTypes = hip_facility.taskTypes.add()
                        hip_facility_taskTypes.other = facility_taskTypes.other
                else: 
                    taskType = hip_facility.taskTypes.add()
                    taskType.other = facility.type
                
                
                hip_facility.simultaneousUsageCount = facility.simultaneousUsageCount
            
            
            taskTypes = self.location.taskTypes
            for taskType in taskTypes:
                hip_taskType = self.location_hip.taskTypes.add()
                hip_taskType.MergeFrom(taskType)
        
            # Create a json location file - this one is compatible with HIP
            json_data = MessageToJson(self.location_hip, including_default_value_fields=False, indent=4)
            with open(file_name, "w") as f:
                f.write(json_data)
            with open("location.dat", "wb") as f:
                f.write(self.location_hip.SerializeToString())    
           #def save_json(self, json_file: str):
            
        else:
            print("No location file was loaded - call: load_location() function ")
        


    def add_DefaultTrainUnitTypes(self):
        """Creates the default train unit types from the data/train_unit_types.json data."""
        train_unit_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train_unit_types.json")
        train_unit_data = json.load(open(train_unit_file, "r"))
        for unit_type in train_unit_data:
            self.add_TrainUnitType(
                self.create_TrainUnitType(
                    displayName=unit_type["name"],
                    carriages=unit_type["carriages"],
                    length=unit_type["length"] / 100, # length in meters
                    combineDuration=unit_type["combineDuration"],
                    splitDuration=unit_type["splitDuration"],
                    typePrefix=unit_type["typePrefix"],
                    needsLoco=unit_type["needsLoco"],
                    isLoco=unit_type["isLoco"],
                    needsElectricity=unit_type["needsElectricity"],
                    # TODO backNormTime, backAdditionTime, travelSpeed, startUpTime
                    idPrefix=None,
                    backNormTime=unit_type["backNormTime"] if "backNormTime" in unit_type else 0,
                    backAdditionTime=unit_type["backAdditionTime"] if "backAdditionTime" in unit_type else 0,
                    travelSpeed=10,
                    startUpTime=0
                )
            )

class ScenarioGeneratorHIP(ScenarioGenerator):
    def __init__(self, standardScenarioGenerator: ScenarioGenerator):
        super().__init__()
        self.scenario_hip = standardScenarioGenerator.scenario_hip
            
    # Converts protobuf object into json representation and saves it into .json file 
    def save_scenario_json(self, file_name: str):
        print("LOG: | call save_scenario_json()|")
        json_data = MessageToJson(self.scenario_hip, including_default_value_fields=False, indent=4)
        with open(file_name, "w") as f:
            f.write(json_data)
        with open("scanario.dat", "wb") as f:
            f.write(self.scenario_hip.SerializeToString())

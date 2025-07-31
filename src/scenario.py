from __future__ import annotations
import sys
import os
import json
import logging
from typing import List
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import ParseDict


sys.path.append(os.path.join(os.path.dirname(__file__), "py_protobuf"))

# Import standard protos (Scenario, Location, TrainUintTypes, Utilities)
import Scenario_pb2
import TrainUnitTypes_pb2
import Location_pb2
import Utilities_pb2

# Import HIP required protos - HIP is name of the solver
import Scenario_HIP_pb2
import Location_HIP_pb2


# To better understand the structure and the parameters/arguments please refer to the Scenario.proto 

class ScenarioGenerator:
    def __init__(self):
        """Initialize the scenario generator, which create a JSON file according to the Scenario.proto structure. The 'hip' file structure is specialized for the robust-rail-solver."""
        self.scenario = Scenario_pb2.Scenario()
        self.scenario_in: List[Scenario_pb2.Train] = []
        self.scenario_out: List[Scenario_pb2.Train] = []

        self.scenario_TrainUnitTypes: List[TrainUnitTypes_pb2.TrainUnitType] = []
        self.scenario_solver =  Scenario_HIP_pb2.Scenario()
        
        # Location where the scenario happens
        self.location = Location_pb2.Location()
        self.location_solver = Location_HIP_pb2.Location()
    
    def save_scenario_json(self, file_name: str):
        # Converts protobuf object into json representation and saves it into .json file 
        json_data = MessageToJson(self.scenario, including_default_value_fields=True, indent=4)
        with open(file_name, "w") as f:
            f.write(json_data)
        logging.info(f"Scenario saved to {file_name}")
            
    def load_scenario(self, file_name):
        with open(file_name, "r") as f:
            json_scenario = json.load(f)
        self.scenario = ParseDict(json_scenario, Scenario_pb2.Scenario())
        
    def create_solver_format_scenario(self, use_scenario=True):
        """Create the solver format of the scenario file. The default source to use is `self.scenario['<attr>']` (use_scenario=True), otherwise we use 'self.scenario_in' and 'self.scenario_out'."""
        if use_scenario:
            incoming_trains_scenario = getattr(self.scenario, "in")
            outgoing_trains_scenario = getattr(self.scenario, "out")
            logging.info("Using `self.scenario.attribute` as the source of the train information")
        else:
            incoming_trains_scenario = self.scenario_in
            outgoing_trains_scenario = self.scenario_out
            logging.info("Using `self.scenario_<attr>` as the source of the train information")
            self.scenario_solver.startTime = self.scenario.startTime
            self.scenario_solver.endTime = self.scenario.endTime            
            logging.info("Copy the start and end time from self.scenario")
        
        # Create the incoming train objects
        incomingTrains = getattr(self.scenario_solver, "in")
        for train_standard in incoming_trains_scenario:
            train = incomingTrains.trains.add()
            train.entryTrackPart = train_standard.sideTrackPart
            train.firstParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.id = train_standard.id
            
            # Collect information of the train unit members of the current train
            members_standard = train_standard.members
            for member in members_standard:
                train_member = train.members.add()
                train_member.trainUnit.id = member.id
                
                # Add the information about service tasks for the individual train units
                for task_standard in member.tasks:
                    task = train_member.tasks.add()
                    if task_standard.type.predefined:
                        task.type.predefined = task_standard.type.predefined
                    elif task_standard.type.other:
                        task.type.other = task_standard.type.other
                    
                    task.priority = task_standard.priority
                    task.duration = task_standard.duration
                
                # Collect the information of the train unit type using the typeDisplayName
                for trainUnitType in self.scenario_TrainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_member.trainUnit.type.displayName = trainUnitType.typePrefix          
                        train_member.trainUnit.type.carriages = trainUnitType.carriages
                        train_member.trainUnit.type.length = trainUnitType.length
                        train_member.trainUnit.type.combineDuration = trainUnitType.combineDuration
                        train_member.trainUnit.type.splitDuration = trainUnitType.splitDuration
                        train_member.trainUnit.type.backNormTime = trainUnitType.backNormTime
                        train_member.trainUnit.type.backAdditionTime = trainUnitType.backAdditionTime

        # Create the outgoing train objects
        trainRequest = getattr(self.scenario_solver, "out")
        for train_standard in outgoing_trains_scenario:
            train = trainRequest.trainRequests.add()
            train.leaveTrackPart = train_standard.sideTrackPart
            train.lastParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.displayName = train_standard.id
            
            # Collect information of the train unit members of the current train
            members_standard = train_standard.members
            for member in members_standard:
                # The Solver format does not use id of the outgoing train units (simply '****')
                train_unit = train.trainUnits.add()
                for trainUnitType in self.scenario_TrainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_unit.type.displayName = trainUnitType.typePrefix          
                        train_unit.type.carriages = trainUnitType.carriages
                        train_unit.type.length = trainUnitType.length
                        train_unit.type.combineDuration = trainUnitType.combineDuration
                        train_unit.type.splitDuration = trainUnitType.splitDuration
                        train_unit.type.backNormTime = trainUnitType.backNormTime
                        train_unit.type.backAdditionTime = trainUnitType.backAdditionTime
        
        # Create the in-standing train objects (train that are already in the yard at the start of the scenario)
        inStandingTrains = getattr(self.scenario_solver, "inStanding")        
        _inStandingTrains = getattr(self.scenario, "inStanding")
        for train_standard in _inStandingTrains:
            train = inStandingTrains.trains.add()
            train.entryTrackPart = train_standard.sideTrackPart
            train.firstParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.id = train_standard.id
            
            # Collect information of the train unit members of the current train
            members_standard = train_standard.members
            for member in members_standard:
                train_member = train.members.add()
                train_member.trainUnit.id = member.id
                
                # Add the information about service tasks for the individual train units
                for task_standard in member.tasks:
                    task = train_member.tasks.add()
                    if task_standard.type.predefined:
                        task.type.predefined = task_standard.type.predefined
                    elif task_standard.type.other:
                        task.type.other = task_standard.type.other
                   
                    task.priority = task_standard.priority
                    task.duration = task_standard.duration
                
                # Collect the information of the train unit type using the typeDisplayName
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_member.trainUnit.type.displayName = trainUnitType.typePrefix          
                        train_member.trainUnit.type.carriages = trainUnitType.carriages
                        train_member.trainUnit.type.length = trainUnitType.length
                        train_member.trainUnit.type.combineDuration = trainUnitType.combineDuration
                        train_member.trainUnit.type.splitDuration = trainUnitType.splitDuration
                        train_member.trainUnit.type.backNormTime = trainUnitType.backNormTime
                        train_member.trainUnit.type.backAdditionTime = trainUnitType.backAdditionTime
                        
        # Create the outstanding train requests: trains that remain in the yard at the end of the scenario
        trainRequest = getattr(self.scenario_solver, "outStanding")
        _outStandingTrains = getattr(self.scenario, "outStanding")
        for train_standard in _outStandingTrains:
            train = trainRequest.trainRequests.add()
            train.leaveTrackPart = train_standard.sideTrackPart
            train.lastParkingTrackPart = train_standard.parkingTrackPart
            train.arrival = train_standard.time
            train.departure = train_standard.time
            train.displayName = train_standard.id

            # Collect information of the train unit members of the current train            
            members_standard = train_standard.members
            for member in members_standard:                
                # The Solver format does not use id of the outgoing train units (simply '****')
                train_unit = train.trainUnits.add()
                for trainUnitType in self.scenario.trainUnitTypes:
                    if trainUnitType.displayName == member.typeDisplayName:
                        train_unit.type.displayName = trainUnitType.typePrefix          
                        train_unit.type.carriages = trainUnitType.carriages
                        train_unit.type.length = trainUnitType.length
                        train_unit.type.combineDuration = trainUnitType.combineDuration
                        train_unit.type.splitDuration = trainUnitType.splitDuration
                        train_unit.type.backNormTime = trainUnitType.backNormTime
                        train_unit.type.backAdditionTime = trainUnitType.backAdditionTime 

    # Add outgoing train to the scenario
    def add_outgoingTrain(self, out_train: Scenario_pb2.Train):
        # Add outgoing train to the scenario        
        trainUnits = out_train.members
        for trainUnit in trainUnits:
            trainUnit.id = "****"
        train = self.scenario.out.add()
        train.MergeFrom(out_train)
        self.scenario_out.append(out_train)
    
    def add_incomingTrain(self, in_train: Scenario_pb2.Train):
        # Add incoming Train to the scenario
        train = getattr(self.scenario, "in").add()
        train.MergeFrom(in_train)
        self.scenario_in.append(in_train)
        
    def add_inStandingTrain(self, in_standingTrain: Scenario_pb2.Train):
        # Add inStanding Train to the scenario
        train = self.scenario.inStanding.add()
        train.MergeFrom(in_standingTrain)
        
    def add_outStandingTrain(self, out_standingTrain: Scenario_pb2.Train):
        # Add outStanding Train to the scenario
        trainUnits = out_standingTrain.members
        for trainUnit in trainUnits:
            trainUnit.id = "****"
        train = self.scenario.outStanding.add()
        train.MergeFrom(out_standingTrain)
        
    def add_nonServiceTraffic(self, nonServiceTraffic: Scenario_pb2.NonServiceTraffic):
        # Add nonServiceTraffic to the scenario
        service = self.scenario.nonServiceTraffic.add()
        service.MergeFrom(nonServiceTraffic)
        
    def add_disabledTrackPart(self, disabledTrackPart: Scenario_pb2.DisabledTrackPart):
        # Add disabledTrackPart to the scenario
        track_part = self.scenario.disabledTrackPart.add()
        track_part.MergeFrom(disabledTrackPart)
        
    def add_workers(self, workers: Scenario_pb2.MemberOfStaff):
        # Add MemberOfStaff to the scenario
        staff = self.scenario.workers.add()
        staff.MergeFrom(workers)
    
    def add_start_and_end_times(self, start: int, end: int):
        # Add startTime and endTime to scenario
        self.scenario.startTime = start
        self.scenario.endTime = end
        
    def add_TrainUnitType(self, trainUnitType: TrainUnitTypes_pb2.TrainUnitType):
        # Add TrainUnitType to scenario    
        trainUnitTypes = self.scenario.trainUnitTypes.add()
        trainUnitTypes.MergeFrom(trainUnitType)
        self.scenario_TrainUnitTypes.append(trainUnitType)
        
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
        task_spec = Scenario_pb2.TaskSpec()        
        # Since taskType is a protobuf object its content must be copied to the other proto object
        # indeed it is a nested message structure => TaskSpec contains TaskType message 
        task_spec.type.CopyFrom(taskType)
        task_spec.priority = priority
        task_spec.duration = duration
        task_spec.requiredSkills.MergeFrom(requiredSkills)
        return task_spec
        
    def create_TrainUnit(self, id: str, typeDisplayName: str, tasks: List[Scenario_pb2.TaskSpec]):
        """_summary_
        Creates a train unit object with specific member id.

        Args:
            id (str):  A unique identifier of the unit, e.g. '2401'
            typeDisplayName (str): displayName of the TrainUnitType, e.g. 'SLT4'
            tasks (List[Scenario_pb2.TaskSpec]): Tasks for this train unit

        Returns:
            _type_: represents a combination of carriages which can move independently
        """
        trainUnit = Scenario_pb2.TrainUnit()
        trainUnit.id = id
        trainUnit.typeDisplayName = typeDisplayName
        trainUnit.tasks.MergeFrom(tasks)
        return trainUnit

    def create_TrainUnitUnmatchedMembers(self, typeDisplayName: str):
        """_summary_
        Creates a train unit object with no specific member (no ids), used for outgoing train requests.

        Args:
            typeDisplayName (str): displayName of the TrainUnitType, e.g. 'SLT4'

        Returns:
            _type_: represents a combination of carriages which can move independently
        """
        trainUnit = Scenario_pb2.TrainUnit()        
        trainUnit.id = "****"
        trainUnit.typeDisplayName = typeDisplayName
        return trainUnit
        

    def create_TaskType(self, predefinedTaskType: int = None, other: str = None)->Location_pb2.TaskType:
        """_summary_
        Create a task type, of the tasks assigned to train units. Matches the predefined task type. e.g., "type" : {"other" : "inwendige_reiniging"}

        Args:
            predefinedTaskType (int, optional):  If the task type maps to one of PredefinedTaskType, use this type here. Defaults to None.
            other (str, optional): Otherwise, specify a custom name. Defaults to None.

        Raises:
            ValueError: If non of them defined

        Returns:
            Location_pb2.TaskType: Specifies the task type - PredefinedTaskType {Move, Split, Combine, Wait, Arrive, Exit, Walking, Break, NonService, BeginMove, EndMove}
        """
        task_type = Location_pb2.TaskType()        
        if predefinedTaskType:
            task_type.predefined = predefinedTaskType
            return task_type
        elif other:
            task_type.other = other
            return task_type
        else:
            raise ValueError("Either 'predefinedTaskType' or 'other' must be provided.")

    def create_NonServiceTraffic(self, members: List[int], arrival: int, departure: int, id: str)->Scenario_pb2.NonServiceTraffic:
        # TODO: what is this used for
        """_summary_

        Args:
            members (List[int]): reserved part of the location send in track parts
            arrival (int): Arrival on the track (Times are in seconds since the epoch)
            departure (int):  departure from the track (Times are in seconds since the epoch)
            id (str): unique identifier

        Returns:
            Scenario_pb2.NonServiceTraffic: Traffic without service
        """
        nonServiceTraffic = Scenario_pb2.NonServiceTraffic()
        nonServiceTraffic.members.extend(members)
        nonServiceTraffic.arrival = arrival
        nonServiceTraffic.departure = departure
        nonServiceTraffic.id = id
        return nonServiceTraffic
    
    def create_DisabledTrackPart(self, trackPart: int = None, arrival: int = None, departure: int = None)->Scenario_pb2.DisabledTrackPart:
        # Create and incoming magic train
        # TODO : what is this used for
        """_summary_

        Args:
            trackPart (int, optional): TrackPart ID of the location this train fetches wizards from, using 9.75 as default doesn't work.. Defaults to None.
            arrival (int, optional):  Arrival on the track. Defaults to None.
            departure (int, optional): departure from the track. Defaults to None.

        Returns:
            Scenario_pb2.DisabledTrackPart: An incoming magic train

        """        
        disabled_trackpart = Scenario_pb2.DisabledTrackPart()
        if trackPart:
            disabled_trackpart.trackPart = trackPart
        if arrival:
            disabled_trackpart.arrival = arrival
        if departure:
            disabled_trackpart.departure = departure
        return disabled_trackpart

    def create_TimeInterval(self, start: float = None, end: float = None)->Utilities_pb2.TimeInterval:
        """_summary_
        Create the time interval of the scenario.
        Args:
            start (float, optional):  Start of the interval in seconds since the epoch. Defaults to None.
            end (float, optional): End of the interval in seconds since the epoch. Defaults to None.

        Returns:
            Utilities_pb2.TimeInterval: representing a single time interval.
        """
        timeInterval = Utilities_pb2.TimeInterval()
        if start:
            timeInterval.start = start
        if end:
            timeInterval.end = end
        return timeInterval            
     
    def create_MemberOfStaff(self, id: int = None, type: str = None, skills: List[str] = None, shifts: List[Utilities_pb2.TimeInterval] = None, breakWindows: List[Utilities_pb2.TimeInterval] = None, breakDuration: float = None, startLocationId: int = None, endLocationId: int = None, canMoveTrains: bool = None, name: str = None, breakLocationId: int = None)->Scenario_pb2.MemberOfStaff:
        """_summary_
        Create Member of Staff which is a human that is able to perform various tasks at the facility

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
        memberOfStaff = Scenario_pb2.MemberOfStaff()
        if id:
            memberOfStaff.id = id
        if type:
            memberOfStaff.type = type
        if skills:
            memberOfStaff.skills.extend(skills)
        if shifts:
            memberOfStaff.shifts.MergeFrom(shifts)
        if  breakWindows:
            memberOfStaff.breakWindows.MergeFrom(breakWindows)   
        if breakDuration:
            memberOfStaff.breakDuration = breakDuration
        if startLocationId:
            memberOfStaff.startLocationId = startLocationId
        if endLocationId:
            memberOfStaff.endLocationId = endLocationId
        if canMoveTrains:
            memberOfStaff.canMoveTrains = canMoveTrains
        if name:
            memberOfStaff.name = name
        if breakLocationId:
            memberOfStaff.breakLocationId = breakLocationId
        
        return memberOfStaff
    
    def create_TrainUnitType(self, displayName: str, carriages: int, length: float, combineDuration: int, splitDuration: int, backNormTime: int, backAdditionTime: int, travelSpeed: int, startUpTime: int, typePrefix: str, needsLoco: bool, isLoco: bool, needsElectricity: bool, idPrefix: int = None)->TrainUnitTypes_pb2.TrainUnitType:
        """_summary_
        Create the type of train units, of which multiple instances can be created. The type specifies all the train characteristics.

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

    def load_location(self, file_name, location_path):
        # Load json format location  
        if not os.path.isfile(file_name):
            if location_path is None:
                file_name = os.path.join(os.path.dirname(__file__), "..", "data", "locations", f"{file_name}{'.json' if '.json' not in file_name else ''}")
            else:
                file_name = os.path.join(location_path, f"{file_name}{'.json' if '.json' not in file_name else ''}")
        with open(file_name, "r") as f:
            json_location = json.load(f)
        logging.info(f"Loading location from {file_name}")
        self.location = ParseDict(json_location, Location_pb2.Location())

    def convert_location_to_solver_format(self, file_name):
        # Converts a standard location into a solver compatible location file format    
        # Check if self.location is not empty
        if self.location.ListFields():
            trackParts = self.location.trackParts
            # Add each track part to the location
            for trackPart in trackParts:
                solver_trackPart = self.location_solver.trackParts.add()
                solver_trackPart.id = trackPart.id
                
                if trackPart.type == Location_pb2.TrackPartType.Building:
                    logging.warning("Building type cannot be added to Solver format, skipping this track part")
                else:
                   solver_trackPart.type = trackPart.type
                
                solver_trackPart.aSide.MergeFrom(trackPart.aSide)
                solver_trackPart.bSide.MergeFrom(trackPart.bSide)
                solver_trackPart.length = trackPart.length
                solver_trackPart.name = trackPart.name
                solver_trackPart.sawMovementAllowed = trackPart.sawMovementAllowed
                solver_trackPart.parkingAllowed = trackPart.parkingAllowed
                
            # Add each facility to the location
            facilities = self.location.facilities
            for facility in facilities:
                solver_facility = self.location_solver.facilities.add()
                solver_facility.id = facility.id  
                solver_facility.type = facility.type
                solver_facility.relatedTrackParts.MergeFrom(facility.relatedTrackParts)
                solver_facility.simultaneousUsageCount = facility.simultaneousUsageCount
                
                # Add the possible task types of the facility
                if facility.taskTypes:
                    for facility_taskTypes in facility.taskTypes:
                        solver_facility_taskTypes = solver_facility.taskTypes.add()
                        solver_facility_taskTypes.other = facility_taskTypes.other
                else: 
                    taskType = solver_facility.taskTypes.add()
                    taskType.other = facility.type
            
            taskTypes = self.location.taskTypes
            for taskType in taskTypes:
                solver_taskType = self.location_solver.taskTypes.add()
                solver_taskType.MergeFrom(taskType)
        
            # Create a json location file - this one is compatible with the solver format
            json_data = MessageToJson(self.location_solver, including_default_value_fields=False, indent=4)
            with open(file_name, "w") as f:
                f.write(json_data)
            logging.info(f"Successfully converted location to Solver format and saved to {file_name}")
        else:
            logging.warning("No location file was loaded")

    def add_DefaultTrainUnitTypes(self):
        """Creates the default train unit types from the data/train_unit_types.json data."""
        train_unit_file = os.path.join(os.path.dirname(__file__), "..", "data", "train_unit_types.json")
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

class SolverScenarioGenerator(ScenarioGenerator):
    def __init__(self, standardScenarioGenerator: ScenarioGenerator):
        super().__init__()
        self.scenario_solver = standardScenarioGenerator.scenario_solver
    
    # Converts protobuf object into json representation and saves it into .json file 
    def save_scenario_json(self, file_name: str):
        json_data = MessageToJson(self.scenario_solver, including_default_value_fields=False, indent=4)
        with open(file_name, "w") as f:
            f.write(json_data)
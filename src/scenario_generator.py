from __future__ import annotations

import json
import logging
import os
from typing import List, Optional

from __init__ import DATA_DIR
from models import IncomingTrainUnit, PredefinedTaskType, TrainRequest

# Import standard protos (Scenario, Location, TrainUnitTypes, Utilities)
from models.location import Location, TaskType
from models.scenario import (
    IncomingTrain,
    Scenario,
    TaskSpec,
    TrainUnit,
    TrainUnitType,
)


class ScenarioGenerator:
    def __init__(self, start: int, end: int):
        """Initialize the scenario generator, which creates a JSON file according to the unified Scenario schema (see models/scenario.py). The 'hip' file structure is specialized for the robust-rail-solver."""
        # train_unit_types is required on Scenario, so it has to be passed here
        # even though add_train_unit_type populates it later.
        self.scenario = Scenario(start_time=start, end_time=end, train_unit_types=[])

        self.scenario_train_unit_types: List[TrainUnitType] = []

        # Location where the scenario happens
        self.location = None

    def save_scenario_json(self, file_name: str):
        # add_in_standing_train() and friends build self.scenario by mutating
        # its list fields in place, which never runs Pydantic's validators
        # (those only fire on construction, not on list mutation). Round-trip
        # through model_validate so cross-record checks like standing order
        # actually run against the final, fully-populated state before it's
        # written out.
        self.scenario = type(self.scenario).model_validate(self.scenario.model_dump(by_alias=True))
        # Use the Dict step to ensure that 0-values are written
        json_data = self.scenario.to_dict()
        with open(file_name, "w") as f:
            json.dump(json_data, f, indent=4)
            f.write("\n")
        logging.info(f"Scenario saved to {file_name}")

    # Add outgoing train to the scenario
    def add_outgoing_train(self, out_train: TrainRequest):
        # Add outgoing train to the scenario
        self.scenario.out.append(out_train)

    def add_incoming_train(self, in_train: IncomingTrain):
        # Add incoming train to the scenario
        self.scenario.in_.append(in_train)

    def add_in_standing_train(self, in_standing_train: IncomingTrain):
        # Add in_standing train to the scenario
        self.scenario.in_standing.append(in_standing_train)

    def add_out_standing_train(self, out_standing_train: TrainRequest):
        # Add out_standing train to the scenario
        self.scenario.out_standing.append(out_standing_train)

    def add_train_unit_type(self, train_unit_type: TrainUnitType):
        # Add TrainUnitType to scenario
        self.scenario.train_unit_types.append(train_unit_type)
        self.scenario_train_unit_types.append(train_unit_type)

    @staticmethod
    def create_incoming_train(
        side_track_part: int,
        track_part: int,
        time: int,
        id: str,
        members: List[IncomingTrainUnit],
        standing_index: Optional[int] = None,
    ) -> IncomingTrain:
        """Create an incoming train object, added as either an in- or in-standing train.

        Args:
            side_track_part (int): side of the railroad track part that identifies the end of the track, used to claim space on a track (often a bumper, or the next part connected to the railroad)
            track_part (int): railroad track part where this train first parks
            time (int): Arrival on the track (and departure from the bumper), in seconds since the epoch
            id (str): unique identifier of the Train
            members (List[IncomingTrainUnit]): train units in the train
            standing_index (Optional[int]): if train is instanding and there are multiple trains on one track, use this to determine the index of the train on the track, with lower indices at the A-side of the track. Leave unset if there is no preference (or only one train stands on the track).

        Returns:
            IncomingTrain: arriving or already-standing train
        """
        return IncomingTrain(
            entry_track_part=side_track_part,
            first_parking_track_part=track_part,
            arrival=time,
            departure=time,
            id=id,
            members=list(members),
            standing_index=standing_index,
        )

    @staticmethod
    def create_train_request(
        side_track_part: int,
        track_part: int,
        time: int,
        id: str,
        members: List[TrainUnit],
        standing_index: Optional[int] = None,
    ) -> TrainRequest:
        """Create a train request object, added as either an out- or out-standing train.

        For a request with train units that have only a type and no ID, enter the train unit objects created with create_train_unit_unmatched_members().

        Args:
            side_track_part (int): side of the railroad track part that identifies the end of the track, used to claim space on a track (often a bumper, or the next part connected to the railroad)
            track_part (int): railroad track part where this train parks until it leaves
            time (int): Departure from the track (and arrival at the bumper), in seconds since the epoch
            id (str): unique identifier of the Train
            members (List[TrainUnit]): requested train units
            standing_index (Optional[int]): if train is outstanding and there are multiple trains on one track, use this to determine the index of the train on the track, with lower indices at the A-side of the track. Leave unset if there is no preference (or only one train stands on the track).

        Returns:
            TrainRequest: departing or remaining-standing train request
        """
        return TrainRequest(
            leave_track_part=side_track_part,
            last_parking_track_part=track_part,
            arrival=time,
            departure=time,
            id=id,
            train_units=list(members),
            standing_index=standing_index,
        )

    @staticmethod
    def create_task_spec(task_type: TaskType, duration: int, required_skills: List[str]) -> TaskSpec:
        """_summary_

        Args:
            task_type (TaskType): type of the task
            duration (int): time this task takes, in seconds
            required_skills (List[str]): skills required to perform the task. Each entry in the list indicates that a member of staff with the given skill is required.

        Returns:
            TaskSpec: task specification specifies a certain task.
        """
        task_spec = TaskSpec()
        task_spec.type = task_type
        task_spec.duration = duration
        task_spec.required_skills.extend(required_skills)
        return task_spec

    @staticmethod
    def create_incoming_train_unit(
        id: int, type_prefix: str, carriages: int, tasks: List[TaskSpec]
    ) -> IncomingTrainUnit:
        """_summary_
        Creates a train unit object with specific member id.

        Args:
            id (int):  A unique identifier of the unit, e.g. 2401
            type_prefix (str): type_prefix of the TrainUnitType, e.g. 'SLT'
            carriages (int): carriage count of the TrainUnitType, e.g. 4
            tasks (List[TaskSpec]): Tasks for this train unit

        Returns:
            _type_: represents a combination of carriages which can move independently
        """
        return IncomingTrainUnit(id=id, type_prefix=type_prefix, carriages=carriages, tasks=tasks)

    @staticmethod
    def create_train_unit_unmatched_members(type_prefix: str, carriages: int):
        """_summary_
        Creates a train unit object with no specific member (no ids), used for outgoing train requests.

        Args:
            type_prefix (str): type_prefix of the TrainUnitType, e.g. 'SLT'
            carriages (int): carriage count of the TrainUnitType, e.g. 4

        Returns:
            _type_: represents a combination of carriages which can move independently
        """
        return TrainUnit(type_prefix=type_prefix, carriages=carriages)

    @staticmethod
    def create_task_type(predefined_task_type: PredefinedTaskType = None, other: str = None) -> TaskType:
        """_summary_
        Create a task type, of the tasks assigned to train units. Matches the predefined task type. e.g., "type" : {"other" : "inwendige_reiniging"}

        Args:
            predefined_task_type (int, optional):  If the task type maps to one of PredefinedTaskType, use this type here. Defaults to None.
            other (str, optional): Otherwise, specify a custom name. Defaults to None.

        Raises:
            ValueError: If non of them defined

        Returns:
            TaskType: Specifies the task type - PredefinedTaskType {Move, Split, Combine, Wait, Arrive, Exit, Walking, Break, NonService, BeginMove, EndMove}
        """
        return TaskType(predefined=predefined_task_type, other=other)

    @staticmethod
    def create_train_unit_type(
        type_prefix: str,
        carriages: int,
        length: float,
        combine_duration: int,
        split_duration: int,
        back_norm_time: int,
        back_addition_time: int,
        travel_speed: int,
        start_up_time: int,
        needs_loco: bool,
        is_loco: bool,
        needs_electricity: bool,
        id_prefix: int = None,
    ) -> TrainUnitType:
        """_summary_
        Create the type of train units, of which multiple instances can be created. The type specifies all the train characteristics.

        Args:
            type_prefix (str): Type family name of the train unit type, e.g. "SGM" or "SLT" (does not encode carriage count).
            carriages (int):  This is the total number of carriages, including the first and last carriage.
            length (float):  Length of this train unit, in meters
            combine_duration (int):  Time it takes to perform a combine in seconds
            split_duration (int): Time it takes to perform a split in seconds
            back_norm_time (int):  kopmaaktijd = back_norm_time + #carriage * back_addition_time
            back_addition_time (int): _description_
            travel_speed (int):  this is the speed of the train but that is yet to be determined whether that is here or location specific #warning
            start_up_time (int): Startup + Shutdown
            needs_loco (bool):  This TrainUnitType needs a locomotive, e.g. it cannot drive itself
            is_loco (bool): Can pull/push other wagons
            needs_electricity (bool): / This train needs electricity, so it can only drive on electrified track parts
            id_prefix (int, optional):  Prefix of train IDs of this type (i.e., the last two digits are removed).  For example, for SLT-4 this is 24. Defaults to None.

        Returns:
            TrainUnitType: _description_
        """
        train_unit_type = TrainUnitType(
            type_prefix=type_prefix,
            carriages=carriages,
            length=length,
            combine_duration=combine_duration,
            split_duration=split_duration,
            back_norm_time=back_norm_time,
            back_addition_time=back_addition_time,
            travel_speed=travel_speed,
            start_up_time=start_up_time,
            needs_loco=needs_loco,
            is_loco=is_loco,
            needs_electricity=needs_electricity,
        )

        if id_prefix:
            train_unit_type.id_prefix = id_prefix

        return train_unit_type

    def load_location(self, file_name):
        # Load json format location
        with open(file_name, "r") as f:
            json_location = json.load(f)
        logging.info(f"Loading location from {file_name}")
        self.location = Location.model_validate(json_location)

    def add_default_train_unit_types(self):
        """Creates the default train unit types from the `data/default_train_unit_types.json` data."""
        train_unit_file = os.path.join(DATA_DIR, "default_train_unit_types.json")
        train_unit_data = json.load(open(train_unit_file, "r"))
        for unit_type in train_unit_data:
            self.add_train_unit_type(
                self.create_train_unit_type(
                    type_prefix=unit_type["typePrefix"],
                    carriages=unit_type["carriages"],
                    length=unit_type["length"] / 100,  # length in meters
                    combine_duration=unit_type["combineDuration"],
                    split_duration=unit_type["splitDuration"],
                    needs_loco=unit_type["needsLoco"],
                    is_loco=unit_type["isLoco"],
                    needs_electricity=unit_type["needsElectricity"],
                    # TODO back_norm_time, back_addition_time, travel_speed, start_up_time
                    id_prefix=None,
                    back_norm_time=unit_type["backNormTime"] if "backNormTime" in unit_type else 0,
                    back_addition_time=unit_type["backAdditionTime"] if "backAdditionTime" in unit_type else 0,
                    travel_speed=10,
                    start_up_time=0,
                )
            )

    def add_custom_train_unit_types(self, config):
        """Creates the train unit types from the custom data object in the configuration."""
        train_unit_data = config["custom_train_unit_types"]
        for unit_type in train_unit_data:
            self.add_train_unit_type(
                self.create_train_unit_type(
                    type_prefix=unit_type["typePrefix"],
                    carriages=unit_type["carriages"],
                    length=unit_type["length"] / 100,  # length in meters
                    combine_duration=unit_type["combineDuration"],
                    split_duration=unit_type["splitDuration"],
                    needs_loco=unit_type["needsLoco"],
                    is_loco=unit_type["isLoco"],
                    needs_electricity=unit_type["needsElectricity"],
                    # TODO back_norm_time, back_addition_time, travel_speed, start_up_time
                    id_prefix=None,
                    back_norm_time=unit_type["backNormTime"] if "backNormTime" in unit_type else 0,
                    back_addition_time=unit_type["backAdditionTime"] if "backAdditionTime" in unit_type else 0,
                    travel_speed=10,
                    start_up_time=0,
                )
            )

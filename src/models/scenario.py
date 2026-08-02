from __future__ import annotations

import logging
from typing import Optional, Type

from pydantic import Field

from .location import TaskType
from .utilities import RailModel, SchemaVersioned, TimeInterval


class TrainUnitType(RailModel):
    """A type of train unit, e.g. SLT or SGM.

    Identity is (type_prefix, carriages): two TrainUnitType instances with
    the same type prefix and carriage count are considered the same type.

    Note: type_prefix is the type family name only ("SLT", "SGM", "VIRM")
    and does NOT encode carriage count. The old convention of "SLT4" / "SLT6"
    is replaced by type_prefix="SLT" + carriages=4. type_display_name is a
    derived value (type_prefix + "-" + carriages) for display/logging only;
    it is not part of the wire schema.
    """

    type_prefix: str = Field(alias="typePrefix")
    carriages: int

    # Optional: all consumers may omit these if not relevant.
    length: Optional[float] = None
    reversal_duration: Optional[int] = Field(None, alias="reversalDuration")
    # TODO: clarify whether reversal_duration is computed from
    # back_norm_time + carriages * back_addition_time, or is a separate
    # concept. If computed, drop it from the schema.
    combine_duration: Optional[int] = Field(None, alias="combineDuration")
    split_duration: Optional[int] = Field(None, alias="splitDuration")
    back_norm_time: Optional[int] = Field(None, alias="backNormTime")
    back_addition_time: Optional[int] = Field(None, alias="backAdditionTime")

    # Optional: generator/evaluator only.
    travel_speed: Optional[int] = Field(None, alias="travelSpeed")
    # TODO: confirm whether travelSpeed is per-TrainUnitType or per-location.
    start_up_time: Optional[int] = Field(None, alias="startUpTime")
    needs_loco: bool = Field(False, alias="needsLoco")
    is_loco: bool = Field(False, alias="isLoco")
    needs_electricity: bool = Field(False, alias="needsElectricity")
    id_prefix: Optional[int] = Field(None, alias="idPrefix")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrainUnitType):
            return NotImplemented
        return self.type_prefix == other.type_prefix and self.carriages == other.carriages

    def __hash__(self) -> int:
        return hash((self.type_prefix, self.carriages))

    @property
    def type_display_name(self) -> str:
        return f"{self.type_prefix}-{self.carriages}"


class TaskSpec(RailModel):
    """A task to be performed on a train unit.

    Note: priority has been dropped from the unified schema and replaced by
    optional. TORS used priority only as a binary 0/non-zero flag; HIP had
    it marked deprecated and unread.
    """

    type: Optional[TaskType] = None
    duration: Optional[int] = None
    # Optional: evaluator/generator only. Empty list means no personnel required.
    required_skills: list[str] = Field(default_factory=list, alias="requiredSkills")
    # False: task must be completed before the train may exit the yard.
    optional: bool = False


class TrainUnit(RailModel):
    """A combination of carriages that can move independently.

    (type_prefix, carriages) is the lookup key into an entry in
    Scenario.train_unit_types. Embedding the full TrainUnitType is
    intentionally avoided to prevent redundancy and inconsistency.
    """

    type_prefix: str = Field(alias="typePrefix")
    carriages: int
    id: Optional[str] = None
    tasks: Optional[list[TaskSpec]] = None

    @property
    def type_display_name(self) -> str:
        return f"{self.type_prefix}-{self.carriages}"


class IncomingTrainUnit(TrainUnit):
    """A TrainUnit as part of an incoming train, with an id and associated tasks."""

    @classmethod
    def from_train_unit(cls,
                        other: TrainUnit) -> IncomingTrainUnit:
       id = other.id
       tasks = other.tasks or []
       if id is None:
           logging.warning("Creating IncomingTrainUnit from TrainUnit "
                           "without id. Using '****'.")
           id = "****"
       # noinspection PyArgumentList
       return cls(type_prefix=other.type_prefix, carriages=other.carriages, id=id, tasks=tasks)

    id: str = None
    tasks: list[TaskSpec] = Field(default_factory=list)


class IncomingTrain(RailModel):
    """A train arriving at or already present in the shunting yard.

    Used for both in (arriving) and inStanding (already present) trains.
    """

    entry_track_part: int = Field(alias="entryTrackPart")
    first_parking_track_part: int = Field(alias="firstParkingTrackPart")
    # None for standing trains (already present at scenario start).
    arrival: Optional[int] = None
    departure: Optional[int] = None
    id: Optional[str] = None
    members: list[IncomingTrainUnit] = Field(default_factory=list)
    # TODO: confirm whether standing_index should be present on IncomingTrain
    # as well as TrainRequest. The non-HIP proto has it on the flat Train type;
    # the HIP proto only has it on TrainRequest.
    standing_index: Optional[float] = Field(None, alias="standingIndex")


class TrainRequest(RailModel):
    """A request for a train to depart from or remain in the shunting yard.

    Used for both out (departing) and outStanding (remaining) trains.
    """

    leave_track_part: int = Field(alias="leaveTrackPart")
    last_parking_track_part: int = Field(alias="lastParkingTrackPart")
    # None for standing trains (remaining at scenario end).
    arrival: Optional[int] = None
    departure: Optional[int] = None
    display_name: Optional[str] = Field(None, alias="displayName")
    # If a TrainUnit's id is None, any unit of the matching type is acceptable.
    train_units: list[TrainUnit] = Field(default_factory=list, alias="trainUnits")
    standing_index: Optional[float] = Field(None, alias="standingIndex")
    # TODO: confirm whether can_depart_from_any_track (non-HIP only) should
    # be added here for outstanding trains.
    can_depart_from_any_track: Optional[bool] = Field(None, alias="canDepartFromAnyTrack")


class Train(RailModel):
    """TEMPORARY: A train arriving at or already present in the shunting
    yard, or a request for a train to depart from or remain in the shunting
    yard.

    Used for all of in (arriving), inStanding (already present), out
    (departing) and outStanding (remaining) trains.
    """

    side_track_part: int = Field(alias="sideTrackPart")
    parking_track_part: int = Field(alias="parkingTrackPart")
    # None for standing trains (already present at scenario start / remaining
    # at scenario end).
    time: Optional[int] = None
    id: Optional[str] = None
    members: list[TrainUnit] = Field(default_factory=list)
    standing_index: Optional[float] = Field(None, alias="standingIndex")
    can_depart_from_any_track: Optional[bool] = Field(None, alias="canDepartFromAnyTrack")
    minimum_duration: Optional[str] =  Field(None, alias="minimumDuration")


class ShuntingUnit(RailModel):
    """A combination of TrainUnits that moves as a single unit at some point
    in time.

    members is a list of TrainUnit IDs (not embedded objects). Consumers that
    need the full TrainUnit look it up via the scenario.

    Note: standingType has been dropped from the unified schema. StandIn and
    StandOut task types in Plan actions carry this information explicitly.
    """

    id: Optional[str] = None
    # TODO: decide whether members should be IDs (current decision) or embedded
    # TrainUnit objects (as in the HIP proto and C# mid-migration state). The
    # Plan proto embeds a full ShuntingUnit in each Action, so if Action
    # references ShuntingUnit by ID instead, a registry is needed.
    members: list[str] = Field(default_factory=list)
    parent_ids: list[str] = Field(default_factory=list, alias="parentIDs")
    child_ids: list[str] = Field(default_factory=list, alias="childIDs")


class NonServiceTraffic(RailModel):
    """Non-service traffic that reserves part of the infrastructure."""

    members: list[int] = Field(default_factory=list)
    arrival: Optional[int] = None
    departure: Optional[int] = None
    id: Optional[str] = None


class DisabledTrackPart(RailModel):
    """A track part that is unavailable during a time window."""

    track_part: Optional[int] = Field(None, alias="trackPart")
    arrival: Optional[int] = None
    departure: Optional[int] = None


class MemberOfStaff(RailModel):
    """A human able to perform tasks at the facility.

    Optional at the Scenario level; omitted for consumers (e.g. the solver)
    that do not model staff.
    """

    id: Optional[int] = None
    type: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    shifts: list[TimeInterval] = Field(default_factory=list)
    break_windows: list[TimeInterval] = Field(default_factory=list, alias="breakWindows")
    break_duration: Optional[float] = Field(None, alias="breakDuration")
    start_location_id: Optional[int] = Field(None, alias="startLocationId")
    end_location_id: Optional[int] = Field(None, alias="endLocationId")
    break_location_id: Optional[int] = Field(None, alias="breakLocationId")
    can_move_trains: Optional[bool] = Field(None, alias="canMoveTrains")
    name: Optional[str] = None


class Scenario(SchemaVersioned):
    """The daily-varying part of the problem specification: which trains
    arrive, depart, or remain in the shunting yard.

    TODO: decide whether train_unit_types belongs here (normalized, referenced
    by name from TrainUnit) or embedded in each TrainUnit. Current decision:
    here.
    """

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_unset=False)

    def to_json(self, **kwargs) -> str:
        return self.model_dump_json(by_alias=True, exclude_unset=False, **kwargs)

    train_unit_types: list[TrainUnitType] = Field(
        default_factory=list, alias="trainUnitTypes"
    )

    # Trains arriving at and departing from the shunting yard.
    # The HIP-shape split (IncomingTrain / TrainRequest) is used rather than
    # the flat non-HIP Train, which conflated arrival/departure semantics.
    in_: list[IncomingTrain] = Field(default_factory=list, alias="in")
    in_standing: list[IncomingTrain] = Field(default_factory=list, alias="inStanding")
    out: list[TrainRequest] = Field(default_factory=list)
    out_standing: list[TrainRequest] = Field(default_factory=list, alias="outStanding")

    start_time: int = Field(alias="startTime")
    end_time: int = Field(alias="endTime")

    # Optional: generator/evaluator only.
    non_service_traffic: list[NonServiceTraffic] = Field(
        default_factory=list, alias="nonServiceTraffic"
    )
    disabled_track_parts: list[DisabledTrackPart] = Field(
        default_factory=list, alias="disabledTrackPart"
    )
    workers: list[MemberOfStaff] = Field(default_factory=list)


class EvaluatorScenario(SchemaVersioned):
    """TEMPORARY: The daily-varying part of the problem specification: which
    trains arrive, depart, or remain in the shunting yard.  Deprecated, flat
    version of `Scenario`.

    Carries schemaVersion too: this is the shape that today's scenario_*.json
    (the file the evaluator actually reads) is generated from, ahead of the
    Phase 1 scenario unification that retires this class.
    """

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_unset=False)

    def to_json(self, **kwargs) -> str:
        return self.model_dump_json(by_alias=True, exclude_unset=False, **kwargs)

    train_unit_types: list[TrainUnitType] = Field(
        default_factory=list, alias="trainUnitTypes"
    )

    in_: list[Train] = Field(default_factory=list, alias="in")
    in_standing: list[Train] = Field(default_factory=list, alias="inStanding")
    out: list[Train] = Field(default_factory=list)
    out_standing: list[Train] = Field(default_factory=list, alias="outStanding")

    start_time: int = Field(alias="startTime")
    end_time: int = Field(alias="endTime")

    # Optional: generator/evaluator only.
    non_service_traffic: list[NonServiceTraffic] = Field(
        default_factory=list, alias="nonServiceTraffic"
    )
    disabled_track_parts: list[DisabledTrackPart] = Field(
        default_factory=list, alias="disabledTrackPart"
    )
    workers: list[MemberOfStaff] = Field(default_factory=list)

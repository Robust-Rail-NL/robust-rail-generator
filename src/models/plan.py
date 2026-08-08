from __future__ import annotations

from typing import Optional

from pydantic import Field

from .location import Resource, TaskType
from .scenario import ShuntingUnit
from .utilities import RailModel, SchemaVersioned


class Action(RailModel):
    """A single action in a shunting plan.

    For Move actions, location is the destination TrackPart ID and resources
    contains the path. For other actions, location is where the action occurs.

    The units an action involves are the ShuntingUnit's members, all of them.
    There was a trainUnitIds field for naming a subset; it was never written by
    the solver, never read by the evaluator on the HIP path, and null in all 606
    actions of every fixture, so it was removed rather than carried further. Note
    for anyone reintroducing per-action subsets: protobuf repeated fields have no
    presence tracking, so "absent" and "empty" arrive identically and cannot mean
    different things without a deliberate design for it.

    TODO: ShuntingUnit is currently embedded in full. Consider switching to
    an ID reference once the evaluator has access to a ShuntingUnit registry
    derived from the Scenario input.
    """

    start_time: Optional[int] = Field(None, alias="startTime")
    end_time: Optional[int] = Field(None, alias="endTime")
    task_type: Optional[TaskType] = Field(None, alias="taskType")
    shunting_unit: Optional[ShuntingUnit] = Field(None, alias="shuntingUnit")
    location: Optional[int] = None
    resources: list[Resource] = Field(default_factory=list)


class Plan(SchemaVersioned):
    """The output of a shunting algorithm: an ordered list of actions.

    There was a trackParts field here, carrying a copy of the Location's track
    graph because the evaluator supposedly could not reach the original. That
    condition no longer holds — run_evaluator.py passes --path_location
    alongside --path_plan — and in practice nothing ever wrote or read it.
    """

    actions: list[Action] = Field(default_factory=list)

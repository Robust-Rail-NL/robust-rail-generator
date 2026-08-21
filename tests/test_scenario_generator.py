"""Regression tests for the two dead-parameter bugs found while implementing
the typePrefix/carriages rename (see unified-schema-design.md, TrainUnitType
section): create_train_unit_type silently dropped type_prefix, and
add_custom_train_unit_types read the wrong (snake_case) config key.

Also covers ScenarioGenerator building Scenario/IncomingTrain/TrainRequest
directly (see unified-schema-design.md, "Next steps" item 6, and issue #12) --
create_incoming_train/create_train_request replaced the old
create_train + create_solver_format_scenario two-step, so the standing-index
and standing-order-validation checks that used to exercise that conversion
now exercise direct construction instead.
"""

import json

import pytest
from pydantic import ValidationError

from models.scenario import IncomingTrainUnit, TrainUnitType
from scenario_generator import ScenarioGenerator


def make_generator() -> ScenarioGenerator:
    return ScenarioGenerator(start=0, end=1000)


class TestCreateTrainUnitType:
    def test_type_prefix_is_stored_on_the_model(self):
        gen = make_generator()
        unit_type = gen.create_train_unit_type(
            type_prefix="SLT",
            carriages=4,
            length=100.0,
            combine_duration=180,
            split_duration=120,
            back_norm_time=120,
            back_addition_time=16,
            travel_speed=10,
            start_up_time=0,
            needs_loco=False,
            is_loco=False,
            needs_electricity=True,
        )
        assert unit_type.type_prefix == "SLT"
        assert unit_type.carriages == 4


class TestAddCustomTrainUnitTypes:
    def test_reads_camel_case_type_prefix_key(self):
        gen = make_generator()
        config = {
            "custom_train_unit_types": [
                {
                    "name": "SLT-4",
                    "carriages": 4,
                    "length": 10000,
                    "combineDuration": 180,
                    "splitDuration": 120,
                    "needsElectricity": True,
                    "typePrefix": "SLT",
                    "needsLoco": False,
                    "isLoco": False,
                    "backNormTime": 120,
                    "backAdditionTime": 16,
                }
            ]
        }
        gen.add_custom_train_unit_types(config)
        assert len(gen.scenario_train_unit_types) == 1
        added = gen.scenario_train_unit_types[0]
        assert added.type_prefix == "SLT"
        assert added.carriages == 4


class TestCreateIncomingTrainUnit:
    def test_type_prefix_and_carriages_round_trip(self):
        gen = make_generator()
        unit = gen.create_incoming_train_unit(id=2401, type_prefix="SLT", carriages=4, tasks=[])
        assert unit.type_prefix == "SLT"
        assert unit.carriages == 4
        assert unit.id == 2401


class TestCreateTrainUnitUnmatchedMembers:
    def test_type_prefix_and_carriages_round_trip(self):
        gen = make_generator()
        unit = gen.create_train_unit_unmatched_members(type_prefix="VIRM", carriages=6)
        assert unit.type_prefix == "VIRM"
        assert unit.carriages == 6
        assert unit.id is None


class TestCreateIncomingTrain:
    def test_maps_side_and_track_part_to_entry_and_first_parking(self):
        gen = make_generator()
        member = IncomingTrainUnit(type_prefix="SLT", carriages=4, id=1)
        train = gen.create_incoming_train(
            side_track_part=1,
            track_part=5,
            time=100,
            id=1,
            members=[member],
        )
        assert train.entry_track_part == 1
        assert train.first_parking_track_part == 5
        assert train.arrival == 100
        assert train.departure == 100
        assert train.id == 1
        assert train.members == [member]
        assert train.standing_index is None

    def test_standing_index_is_set_when_given(self):
        gen = make_generator()
        train = gen.create_incoming_train(
            side_track_part=1,
            track_part=5,
            time=0,
            id=1,
            members=[],
            standing_index=0,
        )
        assert train.standing_index == 0


class TestCreateTrainRequest:
    def test_maps_side_and_track_part_to_leave_and_last_parking(self):
        gen = make_generator()
        unit = gen.create_train_unit_unmatched_members(type_prefix="SLT", carriages=4)
        train = gen.create_train_request(
            side_track_part=2,
            track_part=6,
            time=900,
            id=1,
            members=[unit],
        )
        assert train.leave_track_part == 2
        assert train.last_parking_track_part == 6
        assert train.arrival == 900
        assert train.departure == 900
        assert train.id == 1
        assert train.train_units == [unit]
        assert train.standing_index is None

    def test_standing_index_is_set_when_given(self):
        gen = make_generator()
        train = gen.create_train_request(
            side_track_part=2,
            track_part=6,
            time=1000,
            id=1,
            members=[],
            standing_index=0,
        )
        assert train.standing_index == 0


class TestAddInStandingAndOutStandingTrainsPropagateStandingIndex:
    """The old create_train + create_solver_format_scenario conversion used
    to drop standing_index entirely, silently discarding real order data
    before the file the solver and evaluator actually read was ever written.
    Now that ScenarioGenerator builds IncomingTrain/TrainRequest directly,
    this covers the same guarantee at the construction site."""

    def test_in_standing_index_survives_construction(self):
        gen = make_generator()
        gen.add_train_unit_type(TrainUnitType(type_prefix="SLT", carriages=4))
        member = IncomingTrainUnit(type_prefix="SLT", carriages=4, id=1)
        train = gen.create_incoming_train(
            side_track_part=1,
            track_part=5,
            time=0,
            id=1,
            members=[member],
            standing_index=0,
        )
        gen.add_in_standing_train(train)
        assert gen.scenario.in_standing[0].standing_index == 0

    def test_out_standing_index_survives_construction(self):
        gen = make_generator()
        gen.add_train_unit_type(TrainUnitType(type_prefix="SLT", carriages=4))
        unit = gen.create_train_unit_unmatched_members(type_prefix="SLT", carriages=4)
        train = gen.create_train_request(
            side_track_part=1,
            track_part=5,
            time=1000,
            id=1,
            members=[unit],
            standing_index=0,
        )
        gen.add_out_standing_train(train)
        assert gen.scenario.out_standing[0].standing_index == 0


class TestSaveScenarioJsonValidatesStandingOrder:
    """ScenarioGenerator builds its scenario by appending to list fields
    (add_in_standing_train et al.), which bypasses Pydantic's model_validator
    entirely -- it only runs at construction, not on list mutation.
    save_scenario_json must force re-validation before writing, or the
    standing-order checks never actually run for any scenario assembled this
    way (i.e. every real scenario)."""

    def _two_instanding_on_one_track(self, standing_index=None):
        gen = make_generator()
        gen.add_train_unit_type(TrainUnitType(type_prefix="SLT", carriages=4))
        for i in (1, 2):
            member = IncomingTrainUnit(type_prefix="SLT", carriages=4, id=i)
            train = gen.create_incoming_train(
                side_track_part=1,
                track_part=5,
                time=0,
                id=i,
                members=[member],
                standing_index=standing_index,
            )
            gen.add_in_standing_train(train)
        return gen

    def test_rejects_unresolved_instanding_collision(self, tmp_path):
        gen = self._two_instanding_on_one_track()
        with pytest.raises(ValidationError):
            gen.save_scenario_json(str(tmp_path / "scenario.json"))

    def test_accepts_and_writes_a_resolved_collision(self, tmp_path):
        gen = make_generator()
        gen.add_train_unit_type(TrainUnitType(type_prefix="SLT", carriages=4))
        for i, idx in ((1, 0), (2, 1)):
            member = IncomingTrainUnit(type_prefix="SLT", carriages=4, id=i)
            train = gen.create_incoming_train(
                side_track_part=1,
                track_part=5,
                time=0,
                id=i,
                members=[member],
                standing_index=idx,
            )
            gen.add_in_standing_train(train)
        path = tmp_path / "scenario.json"
        gen.save_scenario_json(str(path))
        written = json.loads(path.read_text())
        assert [t["standingIndex"] for t in written["inStanding"]] == [0, 1]

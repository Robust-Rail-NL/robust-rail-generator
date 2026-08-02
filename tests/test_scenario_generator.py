"""Regression tests for the two dead-parameter bugs found while implementing
the typePrefix/carriages rename (see unified-schema-design.md, TrainUnitType
section): create_train_unit_type silently dropped type_prefix, and
add_custom_train_unit_types read the wrong (snake_case) config key."""

from scenario import ScenarioGenerator


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

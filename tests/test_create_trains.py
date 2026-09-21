"""create_trains() (src/main.py) builds the four kinds of custom train a config file can declare
- in, out, in_standing, out_standing - directly from config, with no file I/O of its own, so it
needs no extraction to test. It had zero coverage before issue #20."""

from robust_rail_models.scenario import TrainUnitType

from main import create_trains
from scenario_generator import ScenarioGenerator


def make_generator() -> ScenarioGenerator:
    gen = ScenarioGenerator(start=0, end=1000)
    gen.add_train_unit_type(TrainUnitType(type_prefix="SLT", carriages=4, length=50.0))
    return gen


class TestCreateTrainsIncoming:
    def test_an_arriving_train_is_added_to_in_(self):
        gen = make_generator()
        task = gen.create_task_spec(gen.create_task_type(other="clean"), duration=10, required_skills=[])
        config = {
            "custom_train_units": [{"id": 1, "type": "SLT-4", "services": ["clean"]}],
            "custom_trains": [
                {"id": 10, "members": [1], "arrival_track": 5, "arrival_track_side": 1, "arrival_time": 100}
            ],
        }

        create_trains(gen, config, {"clean": task})

        assert len(gen.scenario.in_) == 1
        train = gen.scenario.in_[0]
        assert train.id == 10
        assert train.arrival == 100
        assert train.first_parking_track_part == 5
        assert train.entry_track_part == 1
        assert [u.id for u in train.members] == [1]
        assert train.members[0].tasks == [task]

    def test_an_in_standing_train_is_added_to_in_standing_with_time_zero(self):
        gen = make_generator()
        config = {
            "custom_train_units": [{"id": 1, "type": "SLT-4", "services": []}],
            "custom_trains": [
                {
                    "id": 30,
                    "members": [1],
                    "start_at_track": 5,
                    "start_at_track_side": 1,
                    "parking_index": 2,
                }
            ],
        }

        create_trains(gen, config, {})

        assert len(gen.scenario.in_) == 0
        assert len(gen.scenario.in_standing) == 1
        train = gen.scenario.in_standing[0]
        assert train.id == 30
        assert train.arrival == 0
        assert train.first_parking_track_part == 5
        assert train.entry_track_part == 1
        assert train.standing_index == 2


class TestCreateTrainsOutgoing:
    def test_a_departing_train_is_added_to_out(self):
        gen = make_generator()
        config = {
            "custom_train_units": [],
            "custom_trains": [
                {
                    "id": 20,
                    "member_types": ["SLT-4"],
                    "departure_track": 5,
                    "departure_track_side": 1,
                    "departure_time": 900,
                }
            ],
        }

        create_trains(gen, config, {})

        assert len(gen.scenario.out) == 1
        train = gen.scenario.out[0]
        assert train.id == 20
        assert train.departure == 900
        assert train.last_parking_track_part == 5
        assert train.leave_track_part == 1
        assert [(u.type_prefix, u.carriages) for u in train.train_units] == [("SLT", 4)]

    def test_an_out_standing_train_is_added_to_out_standing_with_time_zero(self):
        gen = make_generator()
        config = {
            "custom_train_units": [],
            "custom_trains": [
                {
                    "id": 40,
                    "member_types": ["SLT-4"],
                    "end_at_track": 5,
                    "end_at_track_side": 1,
                    "parking_index": 3,
                }
            ],
        }

        create_trains(gen, config, {})

        assert len(gen.scenario.out) == 0
        assert len(gen.scenario.out_standing) == 1
        train = gen.scenario.out_standing[0]
        assert train.id == 40
        assert train.departure == 0
        assert train.last_parking_track_part == 5
        assert train.leave_track_part == 1
        assert train.standing_index == 3

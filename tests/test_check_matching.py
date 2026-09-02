"""check_matching reads scenario_generator.scenario.{in_,in_standing,out,out_standing},
which used to be flat Train objects (all sharing .time/.members) but are now
IncomingTrain (.arrival/.departure/.members) and TrainRequest
(.arrival/.departure/.train_units) after retiring EvaluatorScenario (issue
#12). These tests exercise the real attribute names on both shapes so a
leftover .time/.members reference on the TrainRequest side would fail loudly
instead of silently matching zero requests."""

from robust_rail_models.location import Location, TrackPart, TrackPartType
from robust_rail_models.scenario import TrainUnitType

from check_matching import check_matching
from scenario_generator import ScenarioGenerator


def make_generator_with_location() -> ScenarioGenerator:
    gen = ScenarioGenerator(start=0, end=1000)
    gen.location = Location(
        track_parts=[
            TrackPart(id=1, type=TrackPartType.BUMPER),
            TrackPart(
                id=5,
                type=TrackPartType.RAILROAD,
                a_side=[1],
                saw_movement_allowed=True,
                parking_allowed=True,
                length=100.0,
            ),
        ]
    )
    gen.add_train_unit_type(TrainUnitType(type_prefix="SLT", carriages=4, length=50.0))
    return gen


class TestCheckMatching:
    def test_matches_a_single_incoming_train_to_a_single_outgoing_request(self):
        gen = make_generator_with_location()
        member = gen.create_incoming_train_unit(id=1, type_prefix="SLT", carriages=4, tasks=[])
        gen.add_incoming_train(
            gen.create_incoming_train(side_track_part=1, track_part=5, time=0, id=1, members=[member])
        )
        unmatched = gen.create_train_unit_unmatched_members(type_prefix="SLT", carriages=4)
        gen.add_outgoing_train(
            gen.create_train_request(side_track_part=1, track_part=5, time=500, id=2, members=[unmatched])
        )
        assert check_matching(gen) is True

    def test_reports_no_match_for_unmatched_outgoing_type(self):
        gen = make_generator_with_location()
        gen.add_train_unit_type(TrainUnitType(type_prefix="VIRM", carriages=6, length=80.0))
        member = gen.create_incoming_train_unit(id=1, type_prefix="SLT", carriages=4, tasks=[])
        gen.add_incoming_train(
            gen.create_incoming_train(side_track_part=1, track_part=5, time=0, id=1, members=[member])
        )
        unmatched = gen.create_train_unit_unmatched_members(type_prefix="VIRM", carriages=6)
        gen.add_outgoing_train(
            gen.create_train_request(side_track_part=1, track_part=5, time=500, id=2, members=[unmatched])
        )
        assert check_matching(gen) is False

    def test_matches_an_out_standing_request_regardless_of_departure_time(self):
        """outStanding requests are excluded from the arrival/departure time
        ordering check (typ == "outstanding" short-circuits it), so a request
        with an earlier departure than the incoming train's arrival must
        still match."""
        gen = make_generator_with_location()
        member = gen.create_incoming_train_unit(id=1, type_prefix="SLT", carriages=4, tasks=[])
        gen.add_incoming_train(
            gen.create_incoming_train(side_track_part=1, track_part=5, time=500, id=1, members=[member])
        )
        unmatched = gen.create_train_unit_unmatched_members(type_prefix="SLT", carriages=4)
        gen.add_out_standing_train(
            gen.create_train_request(side_track_part=1, track_part=5, time=0, id=2, members=[unmatched])
        )
        assert check_matching(gen) is True

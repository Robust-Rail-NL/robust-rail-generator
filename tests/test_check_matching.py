"""check_matching reads scenario_generator.scenario.{in_,in_standing,out,out_standing},
which used to be flat Train objects (all sharing .time/.members) but are now
IncomingTrain (.arrival/.departure/.members) and TrainRequest
(.arrival/.departure/.train_units) after retiring EvaluatorScenario (issue
#12). These tests exercise the real attribute names on both shapes so a
leftover .time/.members reference on the TrainRequest side would fail loudly
instead of silently matching zero requests."""

from robust_rail_models.location import Location, TrackPart, TrackPartType
from robust_rail_models.scenario import TrainUnitType

from check_matching import check_matching, check_train_lengths
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


class TestCheckTrainLengths:
    """check_train_lengths greedily pairs each train that needs a longer-than-average track with
    the longest track still free. It used to process those trains shortest-first, which can pair
    the longest track with a train short enough not to need it and leave no free track long
    enough for a genuinely longer train - rejecting a scenario that actually fits (8c0433b)."""

    def make_generator(self) -> ScenarioGenerator:
        gen = ScenarioGenerator(start=0, end=1000)
        gen.location = Location(
            track_parts=[
                # Short track, present only to pull avg_track_length down so both trains below
                # count as "long".
                TrackPart(
                    id=1,
                    type=TrackPartType.RAILROAD,
                    name="short",
                    saw_movement_allowed=True,
                    parking_allowed=True,
                    length=50.0,
                ),
                TrackPart(
                    id=2,
                    type=TrackPartType.RAILROAD,
                    name="medium",
                    saw_movement_allowed=True,
                    parking_allowed=True,
                    length=250.0,
                ),
                TrackPart(
                    id=3,
                    type=TrackPartType.RAILROAD,
                    name="long",
                    saw_movement_allowed=True,
                    parking_allowed=True,
                    length=300.0,
                ),
            ]
        )
        gen.add_train_unit_type(TrainUnitType(type_prefix="BIG", carriages=4, length=280.0))
        gen.add_train_unit_type(TrainUnitType(type_prefix="MED", carriages=4, length=240.0))
        return gen

    def test_a_feasible_assignment_of_long_trains_to_tracks_is_accepted(self):
        # avg_track_length = (50+250+300)/3 = 200, so both trains (280, 240) count as long.
        # The only feasible pairing is BIG->"long" (300) and MED->"medium" (250): MED does not
        # fit "long" alone, but BIG does not fit "medium" either, so BIG must claim "long" first.
        gen = self.make_generator()
        big = gen.create_incoming_train_unit(id=1, type_prefix="BIG", carriages=4, tasks=[])
        gen.add_incoming_train(gen.create_incoming_train(side_track_part=1, track_part=1, time=0, id=1, members=[big]))
        med = gen.create_incoming_train_unit(id=2, type_prefix="MED", carriages=4, tasks=[])
        gen.add_incoming_train(gen.create_incoming_train(side_track_part=1, track_part=1, time=0, id=2, members=[med]))

        assert check_train_lengths(gen, use_default_material=False) is True

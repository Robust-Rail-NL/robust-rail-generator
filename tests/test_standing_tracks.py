"""assign_standing_tracks() used to be a plain random.sample() of parkable tracks zipped
against a random.sample() of train ids, which never compared a composition's length to the
length of the track it was put on. Instanding and outstanding trains are declared to sit on a
specific track as one composition, so unlike arriving trains they cannot be split across
tracks to make them fit, and a scenario that parks a 324m train on a 222m track is simply
wrong. These tests pin the fit invariant, and the demotion that keeps it holding when a
composition fits nowhere."""

from robust_rail_models.location import Location, TrackPart, TrackPartType
from robust_rail_models.scenario import TrainUnitType

from random_generator import RandomGenerator
from scenario_generator import ScenarioGenerator

# One unit type, 100m per unit, so a composition of n units is exactly n * 100m long.
UNIT_LENGTH = 100.0


def make_random_generator(track_lengths: list[float]) -> RandomGenerator:
    """A generator whose location has one parkable track per given length.

    Each parkable track gets a bumper on both sides so that get_gateway_tracks(), which runs
    in __init__, finds no gateways and leaves the track list to these tests alone.
    """
    track_parts: list[TrackPart] = []
    next_id = 1
    for length in track_lengths:
        bumper_a, bumper_b, track = next_id, next_id + 1, next_id + 2
        next_id += 3
        track_parts.append(TrackPart(id=bumper_a, type=TrackPartType.BUMPER, b_side=[track]))
        track_parts.append(TrackPart(id=bumper_b, type=TrackPartType.BUMPER, a_side=[track]))
        track_parts.append(
            TrackPart(
                id=track,
                type=TrackPartType.RAILROAD,
                a_side=[bumper_a],
                b_side=[bumper_b],
                saw_movement_allowed=True,
                parking_allowed=True,
                length=length,
            )
        )

    gen = ScenarioGenerator(start=0, end=1000)
    gen.location = Location(track_parts=track_parts)
    gen.add_train_unit_type(TrainUnitType(type_prefix="SLT", carriages=4, length=UNIT_LENGTH))
    config = {"seed": 1, "track_id_map": {part.id: part for part in track_parts}}
    return RandomGenerator(gen, config, gen.location, {"arrival": [], "departure": []})


def make_compositions(generator: RandomGenerator, units_per_train: dict[int, int]) -> dict[int, list]:
    """A composition of `units` SLT-4s for each train id, so its length is units * UNIT_LENGTH."""
    return {
        train_id: [
            generator.scenario_generator.create_incoming_train_unit(
                id=train_id * 100 + i, type_prefix="SLT", carriages=4, tasks=[]
            )
            for i in range(units)
        ]
        for train_id, units in units_per_train.items()
    }


class TestAssignStandingTracks:
    def test_every_standing_train_is_placed_on_a_track_that_fits_it(self):
        # Tracks are picked at random from those that fit, so which train lands where varies and
        # a short train may take a long track a longer train needed. Whatever is placed must fit.
        generator = make_random_generator([150.0, 250.0, 450.0])
        compositions = make_compositions(generator, {0: 1, 1: 2, 2: 4})

        assignment = generator.assign_standing_tracks(compositions.keys(), compositions, 3, set())

        for train_id, track in assignment.items():
            assert len(compositions[train_id]) * UNIT_LENGTH <= track.length

    def test_places_every_requested_train_when_they_all_fit_on_every_track(self):
        generator = make_random_generator([450.0, 450.0, 450.0])
        compositions = make_compositions(generator, {0: 1, 1: 2, 2: 4})

        assignment = generator.assign_standing_tracks(compositions.keys(), compositions, 3, set())

        assert len(assignment) == 3
        assert len(set(track.id for track in assignment.values())) == 3, "each train needs its own track"

    def test_a_composition_that_fits_no_track_is_not_made_standing(self):
        generator = make_random_generator([150.0, 250.0])
        compositions = make_compositions(generator, {0: 10})

        assignment = generator.assign_standing_tracks(compositions.keys(), compositions, 1, set())

        assert assignment == {}

    def test_draws_a_replacement_candidate_when_one_composition_fits_nowhere(self):
        # The oversized train must never be placed, but the requested two standing trains are
        # still reached by drawing the remaining candidates instead.
        generator = make_random_generator([150.0, 250.0, 450.0])
        compositions = make_compositions(generator, {0: 10, 1: 1, 2: 2})

        assignment = generator.assign_standing_tracks(compositions.keys(), compositions, 2, set())

        assert set(assignment) == {1, 2}
        for train_id, track in assignment.items():
            assert len(compositions[train_id]) * UNIT_LENGTH <= track.length

    def test_skips_tracks_used_as_gateways(self):
        generator = make_random_generator([150.0, 450.0])
        long_track = next(part for part in generator.scenario_generator.location.track_parts if part.length == 450.0)
        compositions = make_compositions(generator, {0: 4})

        assignment = generator.assign_standing_tracks(compositions.keys(), compositions, 1, {long_track.id})

        # The only track it would fit on is a gateway, so it cannot be made standing.
        assert assignment == {}

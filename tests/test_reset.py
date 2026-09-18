"""reset() used to unconditionally clear self.train_units_subtypes, but that dict is populated
once from the loaded material before generation starts (see create_scenario_from_config) and is
only re-derived per attempt when a `train_unit_types` sublist is configured. Clearing it
unconditionally meant a retry after reset() found no subtypes to draw from and crashed with a
ZeroDivisionError instead of regenerating - the same bug 6d28af7 fixed for train_unit_types,
still present for train_units_subtypes."""

from robust_rail_models.location import Location, TrackPart, TrackPartType
from robust_rail_models.scenario import TrainUnitType

from random_generator import RandomGenerator
from scenario_generator import ScenarioGenerator


def make_random_generator() -> RandomGenerator:
    bumper, track = 1, 2
    track_parts = [
        TrackPart(id=bumper, type=TrackPartType.BUMPER, b_side=[track]),
        TrackPart(
            id=track,
            type=TrackPartType.RAILROAD,
            a_side=[bumper],
            saw_movement_allowed=True,
            parking_allowed=False,
            length=1000.0,
        ),
    ]
    gen = ScenarioGenerator(start=0, end=10000)
    gen.location = Location(track_parts=track_parts)
    unit_type = TrainUnitType(type_prefix="SLT", carriages=4, length=100.0)
    gen.add_train_unit_type(unit_type)
    config = {"seed": 1, "track_id_map": {part.id: part for part in track_parts}}
    generator = RandomGenerator(gen, config, gen.location, {"arrival": [], "departure": []})
    # main() fills these two in from the loaded material before any composition is generated,
    # same as in test_composition_size.py's make_random_generator().
    generator.train_unit_types = [unit_type]
    generator.train_units_subtypes = {"SLT": ["SLT-4"]}
    return generator


class TestReset:
    def test_reset_keeps_the_loaded_train_units_subtypes(self):
        generator = make_random_generator()

        generator.reset()

        assert generator.train_units_subtypes == {"SLT": ["SLT-4"]}

    def test_retrying_generation_after_reset_does_not_crash(self):
        # A config without a `train_unit_distribution.train_unit_types` sublist never
        # repopulates train_units_subtypes on its own, so this retry relies entirely on
        # reset() leaving it alone.
        generator = make_random_generator()
        config = {
            "seed": 1,
            "number_of_trains": 3,
            "min_time_in_yard": 600,
            "min_gap_on_gateway": 300,
            "mixed_traffic": True,
            "matching": 0,
            "perform_servicing": False,
            "use_default_material": True,
            "train_unit_distribution": {"units_per_composition": [1], "super_type_ratio": 0.5},
        }
        generator.generate_train_units = lambda *args, **kwargs: None
        generator.generate_trains = lambda *args, **kwargs: None

        generator.generate_train_compositions(config, generator.scenario_generator, {})
        generator.reset()
        # Used to raise ZeroDivisionError here: different_types = min(len(subtypes), ...) == 0.
        generator.generate_train_compositions(config, generator.scenario_generator, {})

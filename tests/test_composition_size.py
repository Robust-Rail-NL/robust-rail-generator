"""No composition may hold a unit of 6 or more carriages and more than two units, because that
is longer than the tracks a scenario has to park it on. That rule used to be applied at one spot
only, to 6-carriage units only: the number of units drawn for each *arriving* train in the
`train_unit_distribution` path. The departing trains that `matching: 1` builds by redistributing
those same units, and the 1-3 units drawn per train when no `train_unit_distribution` is given at
all, both went uncapped, so a scenario could still ask for a 3 x VIRM-6 composition. These tests
pin the rule on every path that decides a composition's size, and pin that it cuts nothing else:
a composition that drew only shorter units keeps all three of them, even where a longer unit was
on offer."""

import random

from robust_rail_models.location import Location, TrackPart, TrackPartType
from robust_rail_models.scenario import TrainUnitType

from random_generator import RandomGenerator
from scenario_generator import ScenarioGenerator

# Both a 4- and a 6-carriage subtype, so the super type "VIRM" can produce either.
VIRM_4 = TrainUnitType(type_prefix="VIRM", carriages=4, length=100.0)
VIRM_6 = TrainUnitType(type_prefix="VIRM", carriages=6, length=150.0)
# A super type without a 6-carriage subtype, which must stay uncapped.
SLT_4 = TrainUnitType(type_prefix="SLT", carriages=4, length=100.0)
# Longer than 6 carriages, so it falls under the same limit.
ICNG_8 = TrainUnitType(type_prefix="ICNG", carriages=8, length=200.0)


def make_random_generator(unit_types: list[TrainUnitType], seed: int = 1) -> RandomGenerator:
    """A generator with the given train unit types and a location of one plain gateway track."""
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
    for unit_type in unit_types:
        gen.add_train_unit_type(unit_type)
    config = {"seed": seed, "track_id_map": {part.id: part for part in track_parts}}
    generator = RandomGenerator(gen, config, gen.location, {"arrival": [], "departure": []})
    # main() fills these two in from the loaded material before any composition is generated.
    generator.train_unit_types = list(unit_types)
    generator.train_units_subtypes = {
        u.type_prefix: [sub.type_display_name for sub in unit_types if sub.type_prefix == u.type_prefix]
        for u in unit_types
    }
    return generator


def make_config(number_of_trains: int, distribution: dict | None, seed: int = 1) -> dict:
    config = {
        "seed": seed,
        "number_of_trains": number_of_trains,
        "min_time_in_yard": 600,
        "min_gap_on_gateway": 300,
        "mixed_traffic": True,
        "matching": 1,
        "perform_servicing": False,
        "use_default_material": True,
    }
    if distribution is not None:
        config["train_unit_distribution"] = distribution
    return config


def compositions_of(generator: RandomGenerator, config: dict) -> dict:
    """Run only the composition planning of generate_train_compositions().

    The unit and train creation that follows it needs a full location with gateways, which these
    tests deliberately do not build; what they assert on is the plan that step writes.
    """
    distribution_config = {}

    def capture(number_train_units, servicing, plan, service_tasks):
        distribution_config.update(plan)

    generator.generate_train_units = capture
    generator.generate_trains = lambda config, plan: None
    generator.generate_train_compositions(config, generator.scenario_generator, {})
    return distribution_config


def holds_long_unit(composition: list[str]) -> bool:
    """Whether any unit of this composition has 6 or more carriages, by its "<prefix>-<carriages>" name."""
    return any(int(subtype.rsplit("-", 1)[1]) >= 6 for subtype in composition)


class TestDistributionPath:
    def test_no_arriving_composition_with_a_long_unit_exceeds_two_units(self):
        generator = make_random_generator([VIRM_4, VIRM_6])
        config = make_config(20, {"units_per_composition": [3], "super_type_ratio": 0.5, "matching": 0})

        plan = compositions_of(generator, config)

        for composition in plan["subtypes_per_in_train"]:
            if holds_long_unit(composition):
                assert len(composition) <= 2, composition

    def test_arriving_compositions_that_drew_no_long_unit_keep_three_units(self):
        # VIRM-6 is on offer for every one of these trains, so the rule must not shorten the
        # ones that happened to draw only VIRM-4s.
        generator = make_random_generator([VIRM_4, VIRM_6])
        config = make_config(20, {"units_per_composition": [3], "super_type_ratio": 0.5, "matching": 0})

        plan = compositions_of(generator, config)

        three_unit_compositions = [train for train in plan["subtypes_per_in_train"] if len(train) == 3]
        assert three_unit_compositions, plan["subtypes_per_in_train"]
        assert all(not holds_long_unit(train) for train in three_unit_compositions)

    def test_no_departing_composition_with_a_long_unit_exceeds_two_units(self):
        # matching 1 rebuilds the outgoing trains from the pool of incoming units, which is where
        # a 3-unit VIRM-6 composition used to reappear after the incoming ones had been capped.
        generator = make_random_generator([VIRM_4, VIRM_6])
        config = make_config(20, {"units_per_composition": [3], "super_type_ratio": 0.5, "matching": 1})

        plan = compositions_of(generator, config)

        for composition in plan["subtypes_per_out_train"]:
            if holds_long_unit(composition):
                assert len(composition) <= 2, composition

    def test_every_unit_is_still_placed_on_an_outgoing_train(self):
        # Capping splits the pool into more, shorter trains; none of the units may go missing.
        generator = make_random_generator([VIRM_4, VIRM_6])
        config = make_config(8, {"units_per_composition": [3], "super_type_ratio": 0.5, "matching": 1})

        plan = compositions_of(generator, config)

        units_in = sorted(u for train in plan["subtypes_per_in_train"] for u in train)
        units_out = sorted(u for train in plan["subtypes_per_out_train"] for u in train)
        assert units_in == units_out
        assert plan["number_trains_out"] == len(plan["subtypes_per_out_train"])

    def test_a_super_type_with_only_short_subtypes_is_never_shortened(self):
        generator = make_random_generator([SLT_4])
        config = make_config(6, {"units_per_composition": [3], "super_type_ratio": 0.5, "matching": 0})

        plan = compositions_of(generator, config)

        assert all(len(train) == 3 for train in plan["subtypes_per_in_train"]), plan["subtypes_per_in_train"]


class TestWithoutDistribution:
    def test_long_unit_compositions_are_capped(self):
        # Without a train_unit_distribution every train draws 1-3 units of a single type; over
        # this many trains every type is drawn, and a VIRM-6 draw of 3 must come back capped.
        generator = make_random_generator([VIRM_4, VIRM_6])
        config = make_config(40, None)

        plan = compositions_of(generator, config)

        for unit_type, number_of_units in plan["unit_types_per_train"]:
            if unit_type.carriages >= 6:
                assert number_of_units <= 2
            assert 1 <= number_of_units <= 3

    def test_four_carriage_compositions_still_reach_three_units(self):
        generator = make_random_generator([VIRM_4, VIRM_6])
        config = make_config(40, None)

        plan = compositions_of(generator, config)

        assert any(
            unit_type.carriages == 4 and number_of_units == 3
            for unit_type, number_of_units in plan["unit_types_per_train"]
        )


class TestCapCompositionSize:
    def test_caps_a_composition_that_holds_a_long_unit(self):
        generator = make_random_generator([VIRM_4, VIRM_6, SLT_4, ICNG_8])

        assert generator.cap_composition_size(3, ["VIRM-4", "VIRM-4", "VIRM-6"]) == 2
        assert generator.cap_composition_size(3, ["VIRM-6", "VIRM-6", "VIRM-6"]) == 2

    def test_caps_a_composition_that_holds_a_unit_of_more_than_six_carriages(self):
        generator = make_random_generator([VIRM_4, VIRM_6, SLT_4, ICNG_8])

        assert generator.cap_composition_size(3, ["ICNG-8", "ICNG-8", "ICNG-8"]) == 2
        assert generator.cap_composition_size(3, ["VIRM-4", "VIRM-4", "ICNG-8"]) == 2

    def test_leaves_smaller_and_shorter_unit_compositions_alone(self):
        generator = make_random_generator([VIRM_4, VIRM_6, SLT_4, ICNG_8])

        assert generator.cap_composition_size(1, ["VIRM-6"]) == 1
        assert generator.cap_composition_size(2, ["VIRM-6", "VIRM-6"]) == 2
        # Same super type as VIRM-6, but this composition drew none of them
        assert generator.cap_composition_size(3, ["VIRM-4", "VIRM-4", "VIRM-4"]) == 3
        assert generator.cap_composition_size(3, ["SLT-4", "SLT-4", "SLT-4"]) == 3
        assert generator.cap_composition_size(3, []) == 3

    def test_an_unknown_subtype_name_does_not_cap(self):
        # Unknown names carry no carriage count, so they cannot trigger the rule.
        generator = make_random_generator([VIRM_4, VIRM_6])

        assert generator.cap_composition_size(3, ["does-not-exist"]) == 3


def test_generated_train_unit_types_are_capped_too():
    # Types generated for use_default_material: false are named "unitType<i>-<carriages>" just
    # like the default material, so a generated 6-carriage type falls under the same rule.
    generator = make_random_generator([])
    random.seed(0)
    generator.generate_train_unit_types(20)

    six_carriage = [t.type_display_name for t in generator.train_unit_types if t.carriages == 6]
    assert six_carriage, "expected at least one 6-carriage type among 20 generated types"
    assert generator.cap_composition_size(3, six_carriage[:1]) == 2

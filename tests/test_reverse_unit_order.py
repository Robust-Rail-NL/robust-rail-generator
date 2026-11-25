"""Unit lists are read head-first (index 0 = the unit that leads the train; see
docs/unit-order-convention.md in robust-rail-general). A train that enters and leaves through the
same end of the yard drives in with one unit leading and, unless it turns around, drives out with
the other end leading, so its departure list is the reverse of its arrival list. Keeping the
order would force the units to be split off, shunted around and reassembled. The generator
therefore reverses the unit order of a departing train when it leaves at the same end of the yard
as its units arrived. These tests pin that, including that a departure at the opposite end of a
two-ended yard keeps the order, since a train can drive through there."""

import random

import pytest
from robust_rail_models.location import Location, TrackPart, TrackPartType
from robust_rail_models.scenario import TrainUnitType

from random_generator import RandomGenerator
from scenario_generator import ScenarioGenerator

# Two subtypes of one super type: a composition only draws units of a single super type, so it
# takes two subtypes of it to get a train whose unit order is visible.
SLT_3 = TrainUnitType(type_prefix="SLT", carriages=3, length=50.0)
SLT_4 = TrainUnitType(type_prefix="SLT", carriages=4, length=50.0)


def track(id, type, a_side=(), b_side=(), **kwargs):
    return TrackPart(
        id=id,
        type=type,
        a_side=list(a_side),
        b_side=list(b_side),
        saw_movement_allowed=type == TrackPartType.RAILROAD,
        length=kwargs.pop("length", 250.0),
        **kwargs,
    )


def simple_service_tracks() -> dict[int, TrackPart]:
    """SimpleService: tracks 2 and 3 hang off switch 20 at one end of rail_1, tracks 4 and 5 off
    switch 21 at the other end. Every gateway track ends in a bumper of its own."""
    rail, switch = TrackPartType.RAILROAD, TrackPartType.SWITCH
    parts = [
        track(10, TrackPartType.BUMPER, a_side=[5], length=0.0),
        track(11, TrackPartType.BUMPER, b_side=[2], length=0.0),
        track(12, TrackPartType.BUMPER, b_side=[3], length=0.0),
        track(13, TrackPartType.BUMPER, a_side=[4], length=0.0),
        track(1, rail, a_side=[20], b_side=[21], length=1000.0, parking_allowed=True),
        track(2, rail, a_side=[11], b_side=[20], parking_allowed=True),
        track(3, rail, a_side=[12], b_side=[20], parking_allowed=True),
        track(4, rail, a_side=[21], b_side=[13], parking_allowed=True),
        track(5, rail, a_side=[21], b_side=[10], parking_allowed=True),
        track(20, switch, a_side=[3, 2], b_side=[1], length=0.0),
        track(21, switch, a_side=[1], b_side=[4, 5], length=0.0),
    ]
    return {part.id: part for part in parts}


def make_generator(arrival_gateways: list[int], departure_gateways: list[int], seed: int = 1) -> RandomGenerator:
    """A generator on the SimpleService tracks that arrives at and departs from the given gateway
    tracks only."""
    parts = simple_service_tracks()
    bumper_of = {2: 11, 3: 12, 4: 13, 5: 10}

    def gateways(ids):
        return [(parts[i], parts[bumper_of[i]]) for i in ids]

    gen = ScenarioGenerator(start=0, end=100000)
    gen.location = Location(track_parts=list(parts.values()))
    unit_types = [SLT_3, SLT_4]
    for unit_type in unit_types:
        gen.add_train_unit_type(unit_type)
    config = {"seed": seed, "track_id_map": parts}
    generator = RandomGenerator(
        gen, config, gen.location, {"arrival": gateways(arrival_gateways), "departure": gateways(departure_gateways)}
    )
    generator.train_unit_types = list(unit_types)
    generator.train_units_subtypes = {"SLT": [u.type_display_name for u in unit_types]}
    return generator


def generate(generator: RandomGenerator, matching: int | str, trains: int = 6):
    """Run the full train generation; return the type names of every arriving and departing train,
    keyed by train id."""
    config = {
        "seed": 1,
        "number_of_trains": trains,
        "min_time_in_yard": 600,
        "min_gap_on_gateway": 300,
        "mixed_traffic": True,
        "matching": matching,
        "perform_servicing": False,
        "use_default_material": True,
        "train_unit_distribution": {"units_per_composition": [2, 3], "super_type_ratio": 1.0},
    }
    generator.generate_train_compositions(config, generator.scenario_generator, {})
    scenario = generator.scenario_generator.scenario
    arriving = {t.id: [u.type_display_name for u in t.members] for t in scenario.in_}
    departing = {t.id: [u.type_display_name for u in t.train_units] for t in scenario.out}
    return arriving, departing


def has_mixed_trains(trains: dict) -> bool:
    return any(len(set(types)) > 1 for types in trains.values())


class TestSingleEndedYard:
    """Arrival and departure gateways 2 and 3 both hang off switch 20: every departure is at the
    end its units arrived at."""

    def test_departures_list_the_units_in_reverse_with_matching_0(self):
        arriving, departing = generate(make_generator([2, 3], [2, 3]), matching=0)

        assert has_mixed_trains(arriving), arriving
        for train_id, types in arriving.items():
            assert departing[train_id + len(arriving)] == types[::-1]

    def test_departures_are_the_arrivals_reversed_in_train_order_and_unit_order_with_matching_2(self):
        arriving, departing = generate(make_generator([2, 3], [2, 3]), matching=2)

        assert has_mixed_trains(arriving), arriving
        n = len(arriving)
        for train_id, types in arriving.items():
            # matching 2 pairs arriving train i with departing train n - 1 - i
            assert departing[n + (n - 1 - train_id)] == types[::-1]

    @pytest.mark.parametrize("name, legacy", [("FIFO", 0), ("LIFO", 2)])
    def test_a_matching_name_generates_what_its_legacy_integer_does(self, name, legacy):
        assert generate(make_generator([2, 3], [2, 3]), matching=name) == generate(
            make_generator([2, 3], [2, 3]), matching=legacy
        )

    @pytest.mark.parametrize("matching", [0, 1, 2])
    def test_reversal_changes_only_the_order_within_a_departing_train(self, matching, monkeypatch):
        # Same seed and same random calls, so the reversal must not change which units depart
        # where, nor any other random choice (times, gateways).
        with monkeypatch.context() as m:
            m.setattr(RandomGenerator, "should_reverse_units", staticmethod(lambda *args: False))
            _, plain = generate(make_generator([2, 3], [2, 3]), matching=matching)
        _, reversed_ = generate(make_generator([2, 3], [2, 3]), matching=matching)

        assert plain.keys() == reversed_.keys()
        for train_id, types in plain.items():
            assert reversed_[train_id] == types[::-1]

    def test_matching_1_reverses_each_departing_train_too(self, monkeypatch):
        # Each departing train's units come from several arrivals, but every arrival here is at
        # the same end, so the whole departure is judged at that end.
        arriving, departing = generate(make_generator([2, 3], [2, 3]), matching=1)
        with monkeypatch.context() as m:
            m.setattr(RandomGenerator, "should_reverse_units", staticmethod(lambda *args: False))
            _, plain = generate(make_generator([2, 3], [2, 3]), matching=1)

        assert has_mixed_trains(arriving) or has_mixed_trains(plain)
        for train_id, types in plain.items():
            assert departing[train_id] == types[::-1]


class TestTwoEndedYard:
    def test_a_departure_at_the_opposite_end_keeps_the_arrival_order(self):
        # Arrive at switch 20's end (2, 3), depart at switch 21's end (4, 5): a train can drive through.
        arriving, departing = generate(make_generator([2, 3], [4, 5]), matching=0)

        assert has_mixed_trains(arriving), arriving
        for train_id, types in arriving.items():
            assert departing[train_id + len(arriving)] == types

    def test_departures_are_reversed_only_where_they_leave_at_the_arrival_end(self):
        # Arrive at both ends, depart from both ends. Each departure is reversed if and only if its
        # gateway is at the end its source train arrived at.
        generator = make_generator([2, 3, 4, 5], [2, 3, 4, 5], seed=3)
        random.seed(3)
        arriving, departing = generate(generator, matching=0, trains=12)
        scenario = generator.scenario_generator.scenario
        end_of = {2: 20, 3: 20, 4: 21, 5: 21}
        arrival_end = {t.id: end_of[t.first_parking_track_part] for t in scenario.in_}
        departure_end = {t.id: end_of[t.last_parking_track_part] for t in scenario.out}

        reversed_count = kept_count = 0
        for train_id, types in arriving.items():
            out_id = train_id + len(arriving)
            if len(set(types)) < 2:
                continue  # a train of identical units shows no order
            if arrival_end[train_id] == departure_end[out_id]:
                assert departing[out_id] == types[::-1]
                reversed_count += 1
            else:
                assert departing[out_id] == types
                kept_count += 1
        # Both cases have to occur, or this test proves nothing about one of them.
        assert reversed_count > 0 and kept_count > 0


class TestShouldReverseUnits:
    def test_reverses_when_every_unit_arrived_at_the_departure_end(self):
        assert RandomGenerator.should_reverse_units((20,), [(20,), (20,)]) is True

    def test_keeps_the_order_when_the_units_arrived_at_another_end(self):
        assert RandomGenerator.should_reverse_units((21,), [(20,), (20,)]) is False

    def test_the_end_most_units_arrived_at_decides(self):
        assert RandomGenerator.should_reverse_units((20,), [(21,), (20,), (20,)]) is True
        assert RandomGenerator.should_reverse_units((20,), [(21,), (21,), (20,)]) is False

    def test_a_tie_goes_to_the_end_of_the_first_unit(self):
        assert RandomGenerator.should_reverse_units((21,), [(21,), (20,)]) is True
        assert RandomGenerator.should_reverse_units((21,), [(20,), (21,)]) is False

    def test_units_without_an_arrival_gateway_are_ignored(self):
        assert RandomGenerator.should_reverse_units((20,), [None, (20,)]) is True

    def test_keeps_the_order_when_no_unit_arrived_through_a_gateway(self):
        assert RandomGenerator.should_reverse_units((20,), [None, None]) is False


class TestGatewayEnd:
    def test_is_the_connection_away_from_the_bumper(self):
        parts = simple_service_tracks()
        assert RandomGenerator.gateway_end(parts[2], parts[11]) == (20,)  # bumper on the A side
        assert RandomGenerator.gateway_end(parts[4], parts[13]) == (21,)  # bumper on the B side

    def test_gateways_at_one_switch_share_an_end_and_those_at_the_other_do_not(self):
        parts = simple_service_tracks()
        end = RandomGenerator.gateway_end
        assert end(parts[2], parts[11]) == end(parts[3], parts[12])
        assert end(parts[2], parts[11]) != end(parts[4], parts[13])

    def test_raises_when_the_gateway_has_no_track_part_away_from_the_bumper(self):
        parts = simple_service_tracks()
        isolated = track(30, TrackPartType.RAILROAD, a_side=[11], b_side=[])
        with pytest.raises(ValueError, match="needs support added"):
            RandomGenerator.gateway_end(isolated, parts[11])

    def test_raises_when_the_bumper_is_not_next_to_the_gateway(self):
        parts = simple_service_tracks()
        with pytest.raises(ValueError, match="Cannot tell which end"):
            RandomGenerator.gateway_end(parts[2], parts[13])

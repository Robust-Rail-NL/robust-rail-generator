"""assign_arrival_departure_times() guards its departure draws with a GenerationAttemptFailed
when there aren't enough slots for the requested number of trains, so main.py's retry loop can
catch it and try again. The initial arrival draw in both the mixed-traffic and non-mixed-traffic
branches was left unguarded: too many trains for the arrival window raised a raw
`ValueError: Sample larger than population or is negative` from random.sample() instead, which
main.py's retry loop does not catch, crashing the whole run rather than rejecting the attempt."""

from types import SimpleNamespace

import pytest
from robust_rail_models.location import Location

from __init__ import DEFAULT_SERVICING_TRAVEL_ALLOWANCE
from random_generator import GenerationAttemptFailed, RandomGenerator
from scenario_generator import ScenarioGenerator


def make_random_generator(start: int, end: int) -> RandomGenerator:
    gen = ScenarioGenerator(start=start, end=end)
    gen.location = Location(track_parts=[])
    config = {"seed": 1, "track_id_map": {}}
    return RandomGenerator(gen, config, gen.location, {"arrival": [], "departure": []})


class TestNonMixedTrafficArrivalGuard:
    def test_too_many_trains_for_the_arrival_window_raises_generation_attempt_failed(self):
        # start=0, end=1000 -> halfway=500, gap=100 leaves only 5 arrival slots.
        generator = make_random_generator(0, 1000)
        distribution_config = {
            "mixed_traffic": False,
            "min_gap_on_gateway": 100,
            "number_trains_in": 10,
            "number_trains_out": 10,
            "min_time_in_yard": 100,
            "average_servicing_time": 0,
        }

        with pytest.raises(GenerationAttemptFailed):
            generator.assign_arrival_departure_times(distribution_config)

    def test_enough_slots_still_succeeds(self):
        generator = make_random_generator(0, 1000)
        distribution_config = {
            "mixed_traffic": False,
            "min_gap_on_gateway": 100,
            "number_trains_in": 3,
            "number_trains_out": 3,
            "min_time_in_yard": 100,
            "average_servicing_time": 0,
        }

        arrival_times, departure_times = generator.assign_arrival_departure_times(distribution_config)

        assert len(arrival_times) == 3
        assert len(departure_times) == 3


class TestMixedTrafficArrivalGuard:
    def test_too_many_trains_for_the_arrival_window_raises_generation_attempt_failed(self):
        # start=0, end=1000 -> 2/3 of end_time is 666, gap=100 leaves only 7 arrival slots.
        generator = make_random_generator(0, 1000)
        distribution_config = {
            "mixed_traffic": True,
            "min_gap_on_gateway": 100,
            "number_trains_in": 10,
            "number_trains_out": 10,
            "min_time_in_yard": 100,
            "average_servicing_time": 0,
        }

        with pytest.raises(GenerationAttemptFailed):
            generator.assign_arrival_departure_times(distribution_config)

    def test_enough_slots_still_succeeds(self):
        generator = make_random_generator(0, 1000)
        distribution_config = {
            "mixed_traffic": True,
            "min_gap_on_gateway": 100,
            "number_trains_in": 3,
            "number_trains_out": 3,
            "min_time_in_yard": 100,
            "average_servicing_time": 0,
        }

        arrival_times, departure_times = generator.assign_arrival_departure_times(distribution_config)

        assert len(arrival_times) == 3
        assert len(departure_times) == 3


class FakeUnit:
    def __init__(self, *durations):
        self.tasks = [SimpleNamespace(duration=d, type=SimpleNamespace(other="Wasmachine")) for d in durations]


class TestNonMixedTrafficServicingMargin:
    """Without servicing, departures only had to trail the last arrival by min_gap_on_gateway, so a
    unit with a 900 s wash could be due out 960 s after arriving, less than the travel to the
    facility alone. The window now also leaves the unit's longest task total plus the travel
    allowance."""

    def distribution_config(self, **extra):
        return {
            "mixed_traffic": False,
            "min_gap_on_gateway": 100,
            "number_trains_in": 3,
            "number_trains_out": 3,
            "min_time_in_yard": 100,
            "average_servicing_time": 0,
            **extra,
        }

    def test_departures_trail_the_last_arrival_by_the_servicing_margin(self):
        generator = make_random_generator(0, 10000)
        generator.incoming_train_units = {"T": [FakeUnit(300, 200), FakeUnit(), FakeUnit(400)]}

        arrival_times, departure_times = generator.assign_arrival_departure_times(
            self.distribution_config(servicing_travel_allowance=1000)
        )

        # longest task total is 500, so every departure is at least 100 + 500 + 1000 after the last arrival
        assert min(departure_times) >= max(arrival_times) + 100 + 500 + 1000

    def test_the_fallback_travel_allowance_applies_when_the_location_has_no_such_facility(self):
        generator = make_random_generator(0, 10000)
        generator.incoming_train_units = {"T": [FakeUnit(900)]}

        assert generator.servicing_margin(self.distribution_config()) == 900 + DEFAULT_SERVICING_TRAVEL_ALLOWANCE

    def test_no_servicing_tasks_leave_the_window_unchanged(self):
        generator = make_random_generator(0, 10000)
        generator.incoming_train_units = {"T": [FakeUnit(), FakeUnit()]}

        assert generator.servicing_margin(self.distribution_config()) == 0

    def test_a_window_too_short_for_the_margin_raises_generation_attempt_failed(self):
        generator = make_random_generator(0, 2000)
        generator.incoming_train_units = {"T": [FakeUnit(900)]}

        with pytest.raises(GenerationAttemptFailed):
            generator.assign_arrival_departure_times(self.distribution_config(servicing_travel_allowance=1800))

"""create_scenario_from_config() has no test coverage of its own (it reads config/location from
disk paths), so the bugs fixed in it - the bounded retry loop, GenerationAttemptFailed being
caught and retried, service_tasks being passed on every attempt, and average_servicing_time being
computed for every servicing-tasks path - shipped without regression tests (issue #20). These
tests exercise the retry control flow and the two small pure calculations extracted out of it,
without touching the file-loading parts of create_scenario_from_config()."""

import main
from random_generator import GenerationAttemptFailed


class FakeServiceTask:
    def __init__(self, duration):
        self.duration = duration


class FakeRandomGenerator:
    """Stands in for RandomGenerator: `results` gives one outcome per generate_train_compositions()
    call, either an exception instance to raise or None for a normal return."""

    def __init__(self, results):
        self.results = list(results)
        self.reset_calls = 0
        self.generate_calls = []

    def reset(self):
        self.reset_calls += 1

    def generate_train_compositions(self, config, scenario_generator, service_tasks):
        self.generate_calls.append((config, scenario_generator, service_tasks))
        outcome = self.results.pop(0)
        if isinstance(outcome, Exception):
            raise outcome


class TestComputeAverageServicingTime:
    def test_uses_the_longest_task_divided_by_the_task_count_rounded_up(self):
        # Not a true average: the formula is max(durations) / count, an existing convention this
        # extraction preserves rather than changes.
        service_tasks = {"a": FakeServiceTask(10), "b": FakeServiceTask(15)}

        assert main.compute_average_servicing_time(service_tasks) == 8  # ceil(15 / 2)

    def test_single_task(self):
        service_tasks = {"a": FakeServiceTask(7)}

        assert main.compute_average_servicing_time(service_tasks) == 7


class TestTimeWindowIsSufficient:
    def test_enough_slots_is_sufficient(self):
        config = {"start_time": 0, "end_time": 10000, "min_gap_on_gateway": 100, "number_of_trains": 10}

        assert main.time_window_is_sufficient(config, estimated_servicing_time=0) is True

    def test_too_few_slots_is_insufficient(self):
        config = {"start_time": 0, "end_time": 1000, "min_gap_on_gateway": 100, "number_of_trains": 10}

        assert main.time_window_is_sufficient(config, estimated_servicing_time=0) is False

    def test_servicing_time_eats_into_the_window(self):
        # 1000 total, 100 gap -> 10 slots, exactly 2.1 * 4 trains needs 8.4 -> sufficient without
        # servicing, insufficient once 500s of servicing time is subtracted.
        config = {"start_time": 0, "end_time": 1000, "min_gap_on_gateway": 100, "number_of_trains": 4}

        assert main.time_window_is_sufficient(config, estimated_servicing_time=0) is True
        assert main.time_window_is_sufficient(config, estimated_servicing_time=500) is False


class TestGenerateRandomTrains:
    def test_succeeds_on_the_first_attempt(self, monkeypatch):
        monkeypatch.setattr(main, "check_matching", lambda scenario_generator, use_default_material: True)
        random_generator = FakeRandomGenerator([None])
        config = {"use_default_material": True}

        result = main.generate_random_trains(random_generator, config, "scenario_generator", "service_tasks")

        assert result is True
        assert random_generator.reset_calls == 0
        assert len(random_generator.generate_calls) == 1

    def test_retries_after_generation_attempt_failed_without_giving_up(self, monkeypatch):
        monkeypatch.setattr(main, "check_matching", lambda scenario_generator, use_default_material: True)
        random_generator = FakeRandomGenerator([GenerationAttemptFailed("no slots"), None])
        config = {"use_default_material": True}

        result = main.generate_random_trains(random_generator, config, "scenario_generator", "service_tasks")

        assert result is True
        assert random_generator.reset_calls == 1
        assert len(random_generator.generate_calls) == 2

    def test_retries_when_check_matching_rejects_the_attempt(self, monkeypatch):
        outcomes = iter([False, True])
        monkeypatch.setattr(main, "check_matching", lambda scenario_generator, use_default_material: next(outcomes))
        random_generator = FakeRandomGenerator([None, None])
        config = {"use_default_material": True}

        result = main.generate_random_trains(random_generator, config, "scenario_generator", "service_tasks")

        assert result is True
        assert random_generator.reset_calls == 1
        assert len(random_generator.generate_calls) == 2

    def test_stops_at_max_generation_attempts_and_returns_false(self, monkeypatch):
        monkeypatch.setattr(main, "check_matching", lambda scenario_generator, use_default_material: False)
        random_generator = FakeRandomGenerator([None, None, None])
        config = {"use_default_material": True, "max_generation_attempts": 3}

        result = main.generate_random_trains(random_generator, config, "scenario_generator", "service_tasks")

        assert result is False
        assert len(random_generator.generate_calls) == 3

    def test_passes_the_same_service_tasks_on_every_attempt(self, monkeypatch):
        # Regression for cc41776: generate_train_compositions() was once called without
        # service_tasks on the very first attempt.
        monkeypatch.setattr(main, "check_matching", lambda scenario_generator, use_default_material: True)
        random_generator = FakeRandomGenerator([GenerationAttemptFailed("no slots"), None])
        config = {"use_default_material": True}
        service_tasks = {"a": FakeServiceTask(10)}

        main.generate_random_trains(random_generator, config, "scenario_generator", service_tasks)

        assert all(call[2] is service_tasks for call in random_generator.generate_calls)

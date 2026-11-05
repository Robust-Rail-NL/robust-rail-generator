"""With `reject_infeasible` on, generate_random_trains() redraws a scenario that violates a
necessary servicing bound (see feasibility.py) instead of returning it."""

from test_feasibility import location, sweep_scenario, train_out

from main import generate_random_trains


class FakeScenarioGenerator:
    """Whatever the generator drew is `drawn`; `scenario.to_dict()` and `location.model_dump()`
    are all generate_random_trains() reads from it for the feasibility check."""

    def __init__(self, drawn, loc):
        self.scenario = type("S", (), {"to_dict": lambda self_: drawn[0]})()
        self.location = type("L", (), {"model_dump": lambda self_, by_alias: loc})()


class FakeRandomGenerator:
    def __init__(self, drawn, scenarios):
        self.drawn, self.scenarios, self.calls = drawn, list(scenarios), 0

    def reset(self):
        pass

    def generate_train_compositions(self, config, scenario_generator, service_tasks):
        self.calls += 1
        self.drawn[0] = self.scenarios.pop(0)


def feasible_scenario():
    scenario = sweep_scenario()
    scenario["out"] = [train_out(1, 3180)]
    return scenario


class TestRejectInfeasibleOption:
    def run(self, monkeypatch, scenarios, reject, **config):
        import main

        monkeypatch.setattr(main, "check_matching", lambda scenario_generator, use_default_material: True)
        drawn = [None]
        generator = FakeRandomGenerator(drawn, scenarios)
        config = {"use_default_material": True, "train_unit_distribution": {"reject_infeasible": reject}, **config}
        result = generate_random_trains(generator, config, FakeScenarioGenerator(drawn, location()), {})
        return result, generator.calls

    def test_off_by_default_keeps_an_infeasible_draw(self, monkeypatch):
        result, calls = self.run(monkeypatch, [sweep_scenario()], reject=False)

        assert (result, calls) == (True, 1)

    def test_on_redraws_an_infeasible_draw(self, monkeypatch):
        result, calls = self.run(monkeypatch, [sweep_scenario(), feasible_scenario()], reject=True)

        assert (result, calls) == (True, 2)

    def test_on_gives_up_after_max_generation_attempts(self, monkeypatch):
        result, calls = self.run(monkeypatch, [sweep_scenario()] * 3, reject=True, max_generation_attempts=3)

        assert (result, calls) == (False, 3)

    def test_config_without_the_key_does_not_check(self, monkeypatch):
        import main

        monkeypatch.setattr(main, "check_matching", lambda scenario_generator, use_default_material: True)
        generator = FakeRandomGenerator([None], [sweep_scenario()])

        assert generate_random_trains(generator, {"use_default_material": True}, None, {}) is True

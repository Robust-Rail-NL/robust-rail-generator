"""With `servicing_per_composition` on, servicing_ratio is the fraction of arriving compositions
that are serviced and every unit of a serviced composition gets the same task list, instead of
each unit drawing its own (which could mix e.g. a 900 s and a 300 s task in one composition)."""

import math
import random

from robust_rail_models.location import Location
from robust_rail_models.scenario import TrainUnitType

from random_generator import RandomGenerator
from scenario_generator import ScenarioGenerator

UNITS_PER_TRAIN = [1, 2, 3, 2, 3, 1, 2, 3]


def make_setup(per_composition: bool, ratio=0.5, tasks_per_unit=1, seed=0):
    random.seed(seed)
    gen = ScenarioGenerator(start=0, end=100000)
    gen.location = Location(track_parts=[])
    unit_type = TrainUnitType(type_prefix="SLT", carriages=4, length=100.0)
    gen.add_train_unit_type(unit_type)
    generator = RandomGenerator(gen, {"seed": 1, "track_id_map": {}}, gen.location, {"arrival": [], "departure": []})
    generator.train_unit_types = [unit_type]
    service_tasks = {
        name: gen.create_task_spec(gen.create_task_type(other=name), duration=duration, required_skills=[])
        for name, duration in [("wash", 900), ("check", 300), ("clean", 600)]
    }
    distribution_config = {
        "number_trains_in": len(UNITS_PER_TRAIN),
        "number_trains_out": len(UNITS_PER_TRAIN),
        "matching": 0,
        "servicing_ratio": ratio,
        "tasks_per_train_unit": tasks_per_unit,
        "servicing_per_composition": per_composition,
        "unit_types_per_train": [(unit_type, n) for n in UNITS_PER_TRAIN],
        "average_servicing_time": 0,
    }
    generator.generate_train_units(sum(UNITS_PER_TRAIN), True, distribution_config, service_tasks)
    return generator, distribution_config


def task_lists(composition):
    return [[id(t) for t in unit.tasks] for unit in composition]


class TestAssignTasksPerComposition:
    def test_no_unit_gets_tasks_when_units_are_generated(self):
        generator, _ = make_setup(True)
        units = [u for us in generator.incoming_train_units.values() for u in us]
        assert all(not u.tasks for u in units)

    def test_each_composition_is_unserviced_or_has_identical_tasks_on_all_units(self):
        generator, config = make_setup(True, ratio=0.5, tasks_per_unit=3)
        distribution_in, _ = generator.distribute_train_units(config)
        generator.assign_tasks_per_composition(distribution_in, config)

        serviced = 0
        for composition in distribution_in:
            lists = task_lists(composition)
            assert all(lst == lists[0] for lst in lists)
            if lists[0]:
                serviced += 1
                assert 1 <= len(lists[0]) <= 3
        assert serviced == math.floor(0.5 * len(UNITS_PER_TRAIN))

    def test_task_lists_are_not_shared_between_units(self):
        generator, config = make_setup(True, ratio=1.0)
        distribution_in, _ = generator.distribute_train_units(config)
        generator.assign_tasks_per_composition(distribution_in, config)

        composition = next(c for c in distribution_in if len(c) > 1)
        assert composition[0].tasks is not composition[1].tasks

    def test_servicing_margin_sees_the_new_tasks(self):
        generator, config = make_setup(True, ratio=1.0)
        config["servicing_travel_allowance"] = 50
        assert generator.servicing_margin(config) == 0
        distribution_in, _ = generator.distribute_train_units(config)
        generator.assign_tasks_per_composition(distribution_in, config)

        longest = max(sum(t.duration for t in unit.tasks) for c in distribution_in for unit in c)
        assert generator.servicing_margin(config) == longest + 50

    def test_ratio_zero_services_nothing(self):
        generator, config = make_setup(True, ratio=0.0)
        distribution_in, _ = generator.distribute_train_units(config)
        generator.assign_tasks_per_composition(distribution_in, config)
        assert all(not u.tasks for c in distribution_in for u in c)


class TestFlagOff:
    def test_units_are_serviced_per_unit_as_before(self):
        generator, _ = make_setup(False, ratio=0.5)
        units = sorted((u for us in generator.incoming_train_units.values() for u in us), key=lambda u: u.id)
        serviced = [u for u in units if u.tasks]
        assert len(serviced) == math.floor(0.5 * len(units))
        assert serviced == units[: len(serviced)]

import os

from __init__ import DATA_DIR, REPO_DIR
from main import create_scenario_from_config


def default_example_given_trains():
    # Use the example scenario. Give path, location name, and scenario name
    print("\nCreating scenario with given trains")
    path = DATA_DIR
    config_file = "example_configuration_trains-given.json"
    location_filename = "example_location.json"
    scenario_file = "scenario_trains_given.json"
    create_scenario_from_config(config_file, path, scenario_file, location_filename)


def default_example_random_full_paths():
    # Use the example random configuration. Give full location path and scenario file path
    print("\nCreating scenario with random trains")
    config_file = os.path.join(DATA_DIR, "configurations", "example_configuration_random.json")
    location_filename = os.path.join(DATA_DIR, "example_location.json")
    scenario_file = os.path.join(DATA_DIR, "scenarios", "scenario_trains_random.json")
    create_scenario_from_config(config_file, scenario_file=scenario_file, location_file=location_filename)


def default_using_scenario_planning_KleineBinckhorst():
    # Use the example from the robust-rail-general repo and the default paths there
    print(
        "\nCreating scenario using scenario planning inputs for Kleine Binckhorst.\n>>>Requires robust-rail-general repo at same level as robust-rail-generator<<<"
    )
    config_file = "scenario_config_example1"
    create_scenario_from_config(config_file)


def default_using_scenario_planning_otherLocation():
    # Use the example from robust-rail-general with custom path and scenario file name
    print(
        "\nCreating scenario using scenario planning inputs for other location.\n>>>Requires robust-rail-general repo at same level as robust-rail-generator<<<"
    )
    config_file = "scenario_config_train_cleaning_late.json"
    path = os.path.join(REPO_DIR, "robust-rail-general", "Location_SimpleService")
    create_scenario_from_config(config_file, path=path)


def relative_path():
    print("\nCreating scenario, run from robust-rail-generator/data directory")
    os.chdir(DATA_DIR)
    config_file = "example_configuration.json"
    location_file = "example_location.json"
    scenario_file = "example_scenario.json"
    create_scenario_from_config(config_file, path=".", location_file=location_file, scenario_file=scenario_file)


def self_contained_examples():
    """Examples that only read/write this repo's own data/ — no sibling
    checkout required. CI runs this (see scripts/regenerate_examples.py) to
    catch stale checked-in example output."""
    default_example_given_trains()
    default_example_random_full_paths()
    relative_path()


def cross_repo_examples():
    """Examples that read from the sibling robust-rail-general repo."""
    default_using_scenario_planning_KleineBinckhorst()
    default_using_scenario_planning_otherLocation()


if __name__ == "__main__":
    self_contained_examples()
    cross_repo_examples()

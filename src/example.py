import os 
from main import create_scenario_from_config

def default_example_given_trains():
    # Use the example scenario. Give path, location name, and scenario name
    print("\nCreating scenario with given trains")
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    config_file = "example_configuration_trains-given.json"
    location_filename = "example_location.json"
    scenario_file = "scenario_trains_given.json"
    create_scenario_from_config(config_file, path, scenario_file, location_filename)
 
def default_example_random_full_paths():
    # Use the example random configuration. Give full location path and scenario file path
    print("\nCreating scenario with random trains")
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "configurations", "example_configuration_random.json")
    location_filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "example_location.json")
    scenario_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scenarios", "scenario_trains_given.json")
    create_scenario_from_config(config_file, scenario_file=scenario_file, location_path=location_filename)

def default_using_scenario_planning_KleineBinckhorst():
    # Use the example from the scenario-planning-inputs rpo and the default paths there
    print("\nCreating scenario using scenario planning inputs for Kleine Binckhorst")
    config_file = "scenario_config_example1"
    create_scenario_from_config(config_file)

def default_using_scenario_planning_otherLocation():
    # Use the example from scenario-planning-inputs with custom path and scenario file name
    print("\nCreating scenario using scenario planning inputs for other location.\n>>>Requires scenario-planning-inputs repo at same level as robust-rail-generator<<<")
    config_file = "scenario_config_train_cleaning_late.json"
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scenario-planning-inputs", "Location_SimpleService")
    scenario_file = "scenario_train_cleaning_late"
    create_scenario_from_config(config_file, path=path, scenario_file=scenario_file)

def relative_path():
    print("\nCreating scenario, run from robust-rail-generator/data directory")
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
    config_file = "example_configuration.json"
    location_file = "example_location.json"
    scenario_file = "example_scenario.json"
    create_scenario_from_config(config_file, path=".", location_path=location_file, scenario_file=scenario_file)

if __name__ == "__main__":
    default_example_given_trains()
    default_example_random_full_paths()
    default_using_scenario_planning_KleineBinckhorst()
    default_using_scenario_planning_otherLocation()
    relative_path()

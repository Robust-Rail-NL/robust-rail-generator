# TUSS-Instance-Generator
Generator for scenarios of the Train Unit Shunting and Servicing (TUSS) Problem. The scenarios can be solved by [robust-rail-solver](https://github.com/Robust-Rail-NL/robust-rail-solver). The plans produced by the **robust-rail-solver** can be evaluated by [robust-rail-evaluator](https://github.com/Robust-Rail-NL/robust-rail-evaluator), which also requires the scenarios issued by [**TUSS-Instance-Generator**](https://github.com/Robust-Rail-NL/robust-rail-generator) 

## Getting started
Removed description of conda, which is no longer in use.

This section should now describe how to install dependencies and setting up the environment, probably using `uv` and after we've added a `pyproject.toml`.

# How to use?

The scenario generation can be done by using configuration files. These files specify the details, which can be very elaborate or leave some choices to a random generator. For more information on how to structure such a file, see [How to write a configuration file?](./How%20to%20write%20a%20configuration%20file.md). 
We have also included one example in this repo in the `data` [folder](data/README.md), for more examples see the [scenario-planning-input repository](https://github.com/Robust-Rail-NL/scenario-planning-inputs). The example can be accessed through [example.py](src/example.py).

By default, the [Kleine Binckhorst location](../scenario-planning-inputs/Location_KleineBinckhorst/README.md) is used, which is a shunting yard in the Netherlands. By giving a configuration file name, the location is loaded automatically:
```bash
python src/main.py --config "scenario_config_example1.json"
```

Alternatively, a different `path` parameter can be given to load a configuration file from a different location folder in the scenario-planning-inputs.
```bash
python src/main.py --config "scenario_config_train_cleaning_late.json" --path "../scenario-planning-inputs/Location_SimpleService"
```

Finally, you can also specifically enter a different location filename and name of the scenario file to be created, the location filename will be retrieved from the `path`directory, and the scenario will be created in the `path/scenarios/` directory unless a complete path is specified.
```bash
python src/main.py --config "scenario_config_train_cleaning_late.json" --path "../scenario-planning-inputs/Location_SimpleService" --scenario-file "scenario_result_name.json" --location "location.json"
```

The generator creates two scenarios: `scenario.json` and `scenario_solver.json`, because the robust-rail-solver uses a different format of the scenario `scenario_solver.json` than the robust-rail-evaluator. The `location.json` file used by the generator for the location of the shunting yard, also has two formats.
We also include a script to convert scenarios (and locations) of one format to the other. 
```bash
python src/format_converter.py --location-path "./data/example_location.json"
python src/format_converter.py --scenario-path ./data/example_scenario.json
```

# Repository Structure
This gives an overview of the file structure in this repository. The `data` folder stores only a few example files and should not be used for file storage. It also contains two default information files.

**TODO update with information about Pydantic models, under `src/models`, and the JSON schema under `schema`.**
The `src/models` folder includes the format of a Location, a Scenario, a TrainUnitType and the Utilities of a scenario. The `src` folder contains the main generation files: `main.py` is the main method to call, which uses the `check_config.py` to check the configuration and the `check_matching` to make sure that the generated files are feasible. `scenario.py` houses the main structure of the scenario along with the encoding into Pydantic models. The `random_generator.py` contains all the code for randomly generating scenarios. Finally, `format_converter.py` can be used to convert the regular (evaluator) format into solver format, for both location and scenario files. Finally, `example.py` gives an example for the possible parameters.
```
📦robust-rail-generator
 ┣ 📂data
 ┃ ┣ 📂scenarios
 ┃ ┣ 📂configurations
 ┃ ┃ ┣ 📜config_train_cleaning_late.json
 ┃ ┣ 📜default_servicing_tasks.json
 ┃ ┣ 📜default_train_unit_types.json
 ┃ ┗ 📜location.json
 ┣ 📂src
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜check_config.py
 ┃ ┣ 📜check_matching.py
 ┃ ┣ 📜example.py
 ┃ ┣ 📜format_converter.py
 ┃ ┣ 📜main.py
 ┃ ┣ 📜random_generator.py
 ┃ ┗ 📜scenario.py
 ┣ 📜.gitignore
 ┣ 📜README.md
 ┣ 📜How to write a configuration file.md
 ┗ 📜env.yml
```

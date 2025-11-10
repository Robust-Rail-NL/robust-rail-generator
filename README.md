# TUSS-Instance-Generator
Generator for scenarios of the Train Unit Shunting and Servicing (TUSS) Problem. The scenarios can be solved by [robust-rail-solver](https://github.com/Robust-Rail-NL/robust-rail-solver). The plans produced by the **robust-rail-solver** can be evaluated by [robust-rail-evaluator](https://github.com/Robust-Rail-NL/robust-rail-evaluator), which also requires the scenarios issued by [**TUSS-Instance-Generator**](https://github.com/Robust-Rail-NL/robust-rail-generator) 

## Getting started - Conda Environment
* Create a conda environment
  * If not first time setup, create it with the existing dependencies

    `conda env create -f env.yml`

  * To activate the project environment
    
    `conda activate TUSS_Instance_generator`

  * To deactivate the project environment

    `conda deactivate`

  * To remove `(base)` specification

    `conda config --set auto_activate_base false`

  * To revert the changes

    `conda config --set auto_activate_base true`
  
  * To update `env.yml` (useful after adding a new package into the dependency)

    `conda env update -f env.yml`  
  
  * To save update `env.yml`

    `conda env export --no-builds > env.yml`

## Compile protobufs (optional)
This step is only required when the .proto files are modified. The protobuf files are pre-compiled in [py_protobuf](./src/py_protobuf/).

Compile `Scenario.proto`:

```bash
cd protos
protoc -I=. --python_out=../src/py_protobuf Scenario.proto
protoc -I=. --python_out=../src/py_protobuf Location.proto
protoc -I=. --python_out=../src/py_protobuf TrainUnitTypes.proto
protoc -I=. --python_out=../src/py_protobuf Utilities.proto
```
```bash
cd HIP_protos
protoc -I=. --python_out=../../src/py_protobuf Scenario_HIP.proto
protoc -I=. --python_out=../../src/py_protobuf Location_HIP.proto
```

# How to use ?

The scenario generation can be done by using configuration files. These files specify the details, which can be very elaborate or leave some choices to a random generator. For more information on how to structure such a file, see [How to write a configuration file?](./data/scenario_configurations/How%20to%20write%20a%20configuration%20file.md). 
We have also included some examples, such as an [example with three trains](./data/scenario_configurations/example_config1.json) or an [example with ten randomly generated trains](./data/scenario_configurations/random_config.json).

To create a scenario, run:
```bash
python src/main.py --config "example_config1.json" --scenario-file "custom-named-scenario.json"
```

Do not forget to specify the path to the configuration file `--config "path/to/config.json"`. Optionally, a custom name can be assigned to the generated scenario `--scenario-file "name_of_scenario"`. Moreover, a path can be given where the configuration file can be found, and the scenario can be written to.

For example, (when the robust-rail scenario repository is also included in the project), run:
```bash
python src/main.py --config "scenario_config.json" --path "../scenario-planning-inputs/Scenario_settings/setting_A/"
```
The generator creates two scenarios: `scenario.json` and `scenario_solver.json`, because the robust-rail-solver uses a different format of the scenario `scneario_solver.json` than the robust-rail-evaluator. The `location.json` file used by the generator for the location of the shunting yard, also has two formats.
We also include a script to convert scenarios (and locations) of one format to the other. 
```bash
python src/format_converter.py --location-path "./data/locations/simple_service_location.json"
python src/format_converter.py --scenario-path ./data/scenarios/scenario_kleineBinckhorst_6t_custom_config1.json
```

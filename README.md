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
python src/main.py --config "scenario_config_train_cleaning_late.json" --path "../scenario-planning-inputs/Location_SimpleService" --scenario-file "scenario_result_name.json" --location "location.json""
```

The generator creates two scenarios: `scenario.json` and `scenario_solver.json`, because the robust-rail-solver uses a different format of the scenario `scenario_solver.json` than the robust-rail-evaluator. The `location.json` file used by the generator for the location of the shunting yard, also has two formats.
We also include a script to convert scenarios (and locations) of one format to the other. 
```bash
python src/format_converter.py --location-path "./data/example_location.json"
python src/format_converter.py --scenario-path ./data/example_scenario.json
```

# Repository Structure
This gives an overview of the file structure in this repository. The `data` folder stores only a few example files and should not be used for file storage. It also contains two default information files.

The `protos` folder includes the format of a Location, a Scenario, a TrainUnitType and the Utilities of a scenario. There are also specific ProtoBuf formats for the `HIP` format, which is the solver format. The `src` folder contains the generated pyProtoBuf files, along with the main generation files: `main.py` is the main method to call, which uses the `check_config.py` to check the configuration and the `check_matching` to make sure that the generated files are feasible. `scenario.py` houses the main structure of the scenario along with the encoding into the ProtoBuf format. The `random_generator.py` contains all the code for randomly generating scenarios. Finally, `format_converter.py` can be used to convert the regular (evaluator) format into solver format, for both location and scenario files. Finally, `example.py` gives an example for the possible parameters.
```
📦robust-rail-generator
 ┣ 📂data
 ┃ ┣ 📂scenarios
 ┃ ┣ 📂configurations
 ┃ ┃ ┣ 📜config_train_cleaning_late.json
 ┃ ┣ 📜default_servicing_tasks.json
 ┃ ┣ 📜default_train_unit_types.json
 ┃ ┗ 📜location.json
 ┣ 📂protos
 ┃ ┣ 📂HIP_protos
 ┃ ┃ ┣ 📜Location_HIP.proto
 ┃ ┃ ┗ 📜Scenario_HIP.proto
 ┃ ┣ 📜Location.proto
 ┃ ┣ 📜Scenario.proto
 ┃ ┣ 📜TrainUnitTypes.proto
 ┃ ┗ 📜Utilities.proto
 ┣ 📂src
 ┃ ┣ 📂py_protobuf
 ┃ ┃ ┣ 📜Location_HIP_pb2.py
 ┃ ┃ ┣ 📜Location_pb2.py
 ┃ ┃ ┣ 📜Scenario_HIP_pb2.py
 ┃ ┃ ┣ 📜Scenario_pb2.py
 ┃ ┃ ┣ 📜TrainUnitTypes_pb2.py
 ┃ ┃ ┣ 📜Utilities_pb2.py
 ┃ ┃ ┗ 📜__init__.py
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

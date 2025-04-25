# TUSS-Instance-Generator
Generator for scenarios of the Train Unit Shunting and Servicing Problem. The scenarios can be solved by [robust-rail-solver](https://github.com/Robust-Rail-NL/robust-rail-solver). The plans produced by the **robust-rail-solver** can be evaluated by [robust-rail-evaluator](https://github.com/Robust-Rail-NL/robust-rail-evaluator), which also requires the scenarios issued by [**TUSS-Instance-Generator**](https://github.com/Robust-Rail-NL/robust-rail-generator) 

## Getting started - Conda Environemnt
* Create a conda environemnt
  * If not first time setup, create it with the existing dependencies

    `conda env create -f env.yml`

  * To activate the project environment
    
    `conda activate TUSS_Instance_generator`

  * To deactivate the project environement

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

* [scenario_generator.py](./src/scenario_generator/scenario_generator.py) contains the core functions to generate scenarios.

* [create_scenario.py](./src/scenario_generator/create_scenario.py) allows the creation of scenarios by using configuration files (e.g., [example_config.json](./src/scenario_generator/examples/example_config1.json)). 

* The scenario generation can be done by using configuration files, do not forget to specify the path to the configuration file `--config "path/to/config.json"`. Optionally, a custom name can be assigned to the generated scenario `--scenario-file "name_of_scenario"`.

* The explanation of the configuration is described by [config_explanation.md](./src/scenario_generator/config_explanation.md).

### Example of usage
```bash
cd src/scenario_generator
python create_scenario.py --config "../../examples/example_config1.json" --scenario-file "custom-named-scenario.json"
```

### Some hints for configuration
* `custom_trains` -> are the arriving/in-outstanding/departing trains. *Note:* in-outstanding trains are not yet supported by [robust-rail-solver](https://github.com/Robust-Rail-NL/robust-rail-solver).
* Define arriving train -> `arrival_time`/`arrival_track` must be defined 

* Define departing train -> `departure_time` / `departure_track` must be defined


* Define instanding train -> `start_at_track` must be defined - **Not fully supported yet**

* Define outstanding train -> `end_at_track` must be defined - **Not fully supported yet**

* `custom_trains` - `members` contains one or more train units defined in `custom_train_units`

* Define services - `services` is a list which can be kept empty or using definitions from `custom_servicing_tasks` 


## Run (unit-like) tests

```bash
cd src/scenario_generator/examples
python examples.py
```


## Validated scenarios
Some of the scenarios were successfully solved by [robust-rail-solver](https://github.com/Robust-Rail-NL/robust-rail-solver) and the plans were validated by [robust-rail-evaluator](https://github.com/Robust-Rail-NL/robust-rail-evaluator). *Note* that all these scenarios were run on a [**new version of Kleine Binckhorst location**](data/validated/location/KleineBinckhorst_v2/).


* [**Scenarios:**](data/validated/scenario/KleineBinckhorst_v2/)
  * [**Scenario 6t custom config2**](data/validated/scenario/KleineBinckhorst_v2/scenario_kleineBinckhorst_6t_custom_config2/)
  * [**Scenario 6t custom config3**](data/validated/scenario/KleineBinckhorst_v2/scenario_kleineBinckhorst_6t_custom_config3/)
  * [**Scenario 10t random 42s distribution1**](data/validated/scenario/KleineBinckhorst_v2/scenario_kleineBinckhorst_10t_random_42s_distribution1/)
  * [**Scenario 10t random 42s distribution2**](data/validated/scenario/KleineBinckhorst_v2/scenario_kleineBinckhorst_10t_random_42s_distribution2/)

* [**New version of Kleine Binckhorst location**](data/validated/location/KleineBinckhorst_v2/)
  * [**location for evaluator**](data/validated/location/KleineBinckhorst_v2/location_location_kleineBinckhorst.json)
  * [**location for solver**](data/validated/location/KleineBinckhorst_v2/location_kleineBinckhorst_HIP_dump.json)

* [**Plans**](data/validated/plan/KleineBinckhorst_v2/)
  * [**Plans for Scenario 6t custom config2**](data/validated/plan/KleineBinckhorst_v2/scenario_kleineBinckhorst_6t_custom_config2/plan_scenario_kleineBinckhorst_6t_custom_config2.json)
  * [**Plans for Scenario 6t custom config3**](data/validated/plan/KleineBinckhorst_v2/scenario_kleineBinckhorst_6t_custom_config3/plan_scenario_kleineBinckhorst_6t_custom_config3.json)
  * [**Plans for Scenario 10t random 42s distribution1**](data/validated/plan/KleineBinckhorst_v2/scenario_kleineBinckhorst_10t_random_42s_distribution1/plan_scenario_kleineBinckhorst_10t_random_42s_distribution1.json)
  * [**Plans for Scenario 10t random 42s distribution2**](data/validated/plan/KleineBinckhorst_v2/scenario_kleineBinckhorst_10t_random_42s_distribution2/plan_scenario_kleineBinckhorst_10t_random_42s_distribution2.json)
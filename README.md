# TUSS-Instance-Generator
Generator for scenarios of the Train Unit Shunting and Servicing Problem

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

## Compile protobufs
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

## Run tests

```bash
cd src/scenario_generator/examples
python examples.py
```


## TODOs 
* Probably we have to add a configuration file that helps to define the scenarion generation
    - Suggestion: let's use `.toml` format configuration files 

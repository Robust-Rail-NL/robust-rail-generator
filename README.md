# TUSS-Instance-Generator
Generator for scenarios of the Train Unit Shunting and Servicing (TUSS) Problem. The scenarios can be solved by [robust-rail-solver](https://github.com/Robust-Rail-NL/robust-rail-solver). The plans produced by the **robust-rail-solver** can be evaluated by [robust-rail-evaluator](https://github.com/Robust-Rail-NL/robust-rail-evaluator), which also requires the scenarios issued by [**TUSS-Instance-Generator**](https://github.com/Robust-Rail-NL/robust-rail-generator)

## Getting started

Requires Python 3.12+ and [`uv`](https://docs.astral.sh/uv/). Install the runtime and dev
dependencies (pinned by `uv.lock`) into a local `.venv`:

```bash
uv sync
```

Run the generator, the test suite, or any other project command through `uv run` so it picks up
that environment, e.g. `uv run pytest -q`. This repo also uses [`pre-commit`](https://pre-commit.com/)
for formatting and linting (Ruff); after `uv sync`, install the git hook once with:

```bash
uv run pre-commit install
```

# How to use?

The scenario generation can be done by using configuration files. These files specify the details, which can be very elaborate or leave some choices to a random generator. For more information on how to structure such a file, see [How to write a configuration file?](./How%20to%20write%20a%20configuration%20file.md).
We have also included one example in this repo in the `data` [folder](data/README.md), for more examples see the [scenario-planning-input repository](https://github.com/Robust-Rail-NL/scenario-planning-inputs). The example can be accessed through [example.py](src/example.py).

By default, the [Kleine Binckhorst location](../scenario-planning-inputs/Location_KleineBinckhorst/README.md) is used, which is a shunting yard in the Netherlands. By giving a configuration file name, the location is loaded automatically:
```bash
uv run python src/main.py --config "scenario_config_example1.json"
```

Alternatively, a different `path` parameter can be given to load a configuration file from a different location folder in the scenario-planning-inputs.
```bash
uv run python src/main.py --config "scenario_config_train_cleaning_late.json" --path "../scenario-planning-inputs/Location_SimpleService"
```

Finally, you can also specifically enter a different location filename and name of the scenario file to be created, the location filename will be retrieved from the `path`directory, and the scenario will be created in the `path/scenarios/` directory unless a complete path is specified.
```bash
uv run python src/main.py --config "scenario_config_train_cleaning_late.json" --path "../scenario-planning-inputs/Location_SimpleService" --scenario-file "scenario_result_name.json" --location "location.json"
```

# Repository Structure
This gives an overview of the file structure in this repository. The `data` folder stores only a few example files and should not be used for file storage. It also contains two default information files.

The interchange format is defined by the Pydantic models under `src/models`. JSON Schema for these models is exported to `schema/` via `python3 scripts/export_schema.py`; regenerate it after any change to a model's wire shape.
The `src/models` folder includes the format of a Location, a Scenario, a TrainUnitType and the Utilities of a scenario. The `src` folder contains the main generation files: `main.py` is the main method to call, which uses the `check_config.py` to check the configuration and the `check_matching` to make sure that the generated files are feasible. `scenario.py` houses the main structure of the scenario along with the encoding into Pydantic models. The `random_generator.py` contains all the code for randomly generating scenarios. Finally, `example.py` gives an example for the possible parameters.
```
📦robust-rail-generator
 ┣ 📂data
 ┃ ┣ 📂scenarios
 ┃ ┣ 📂configurations
 ┃ ┃ ┣ 📜config_train_cleaning_late.json
 ┃ ┣ 📜default_servicing_tasks.json
 ┃ ┣ 📜default_train_unit_types.json
 ┃ ┗ 📜location.json
 ┣ 📂schema
 ┃ ┗ 📜 (JSON Schema exported from src/models, see below)
 ┣ 📂scripts
 ┃ ┗ 📜export_schema.py
 ┣ 📂src
 ┃ ┣ 📂models
 ┃ ┃ ┗ 📜 (the Pydantic models — the source of truth for the interchange format)
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜check_config.py
 ┃ ┣ 📜check_matching.py
 ┃ ┣ 📜example.py
 ┃ ┣ 📜main.py
 ┃ ┣ 📜random_generator.py
 ┃ ┗ 📜scenario.py
 ┣ 📂tests
 ┣ 📜.gitignore
 ┣ 📜.pre-commit-config.yaml
 ┣ 📜Dockerfile
 ┣ 📜docker-push.sh
 ┣ 📜How to write a configuration file.md
 ┣ 📜pyproject.toml
 ┣ 📜README.md
 ┣ 📜SCHEMA_CHANGELOG.md
 ┗ 📜uv.lock
```

# Publishing the generator image

The version is tracked in a single place: `pyproject.toml`'s `[project] version`. The Dockerfile's
`org.opencontainers.image.version` label and the image tags pushed to `ghcr.io` are both derived from
this field via a build-arg, so nothing else needs editing by hand.

```sh
./docker-push.sh
```
This builds a multi-arch (`linux/amd64`, `linux/arm64`) image and pushes it to
`ghcr.io/robust-rail-nl/generator`, tagged with the current version and `:latest`.
Multi-arch matters here even though this is a Python image: pydantic v2 bundles `pydantic-core`, a
compiled Rust extension, so the installed wheel — and therefore the image — is architecture-specific.

It requires a `buildx` builder using the `docker-container` driver with `network=host` (needed because
the default driver's isolated network namespace can fail to resolve private/LAN DNS); the script
creates one named `robust-rail-builder` if it doesn't already exist. This builder name is shared with
sibling Robust-Rail-NL projects (e.g. `robust-rail-evaluator`, `robust-rail-solver`) that need the same
setup.

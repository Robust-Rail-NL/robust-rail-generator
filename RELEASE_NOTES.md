# Release notes

## 2.4.0 — 2026-11-04

### `servicing_per_composition` option

New optional boolean in `train_unit_distribution` (default `false`, so existing configs generate the
same scenarios as before). When `true`, `servicing_ratio` is the fraction of arriving compositions
that are serviced, and all units of a serviced composition get the same servicing tasks, instead of
each unit drawing its own. Requires `perform_servicing`.

## 2.3.0 — 2026-11-03

Generated scenarios now use wire-format `schemaVersion` 2, and scenarios that contain servicing
tasks are now actually solvable: the default servicing tasks match the location's facilities, and
departures leave enough time for servicing.

### Scenarios now use `schemaVersion` 2 (`#22`)

The `robust-rail-general` dependency moves from `v0.1.1` to `v0.2.0`, whose
`EXPECTED_SCHEMA_VERSION` is 2. Generated scenario JSON now declares `schemaVersion: 2`, and the
checked-in example fixtures in `data/` were bumped to match. The schema changes themselves are
documented in `robust-rail-general`'s `SCHEMA_CHANGELOG.md`. Consumers of the generated files need a
version of the evaluator/solver that reads schema 2.

Internal docs and a docstring that still used the old `PredefinedTaskType` name (`Walking`/`Setback`)
now say `Reverse`, matching the renamed enum member. No functional change.

### Default servicing tasks are typed by facility (`#23`)

With `perform_servicing` enabled and no `custom_servicing_tasks`, the generated task type was the
key of `default_servicing_tasks.json` (for example `wassen`), but the location's facilities are
typed by `requiredFacility` (for example `Wasmachine`). The planner and the solver match a task to
a facility by that type, so every generated scenario with a default servicing task failed in both.
The task type is now taken from `requiredFacility`, as the `custom_servicing_tasks` path already
did. The example scenario in `data/` was regenerated.

### Departures leave time for servicing (`#25`)

With `mixed_traffic: false`, the departure window started at the last arrival plus
`min_gap_on_gateway`, regardless of the servicing the units needed. A unit that arrived with the
last train could be due out only `min_gap_on_gateway` after arriving (480 s in the poster
configuration), which is less than a single 900 s task, let alone the driving to the facility and
back. No plan can meet such a departure, however long the search runs.

The window now starts at the last arrival, plus `min_gap_on_gateway`, plus a servicing margin: the
longest total task time of any unit, plus a travel allowance.

- The travel allowance is computed from the location: the shortest route gateway, facility,
  gateway over the track graph, priced with the movement model that the evaluator and the solver
  use (`movementTrackCoefficient`, `movementSwitchCoefficient`, a turn-around as one more track
  crossing plus the unit type's reversal duration, and only on tracks that allow saw movement). The
  longest trip over the possible gateways, for the facility types the units need, counts. For
  Kleine Binckhorst this reproduces the 510 s the solver took for its first move to the cleaning
  platform. It ignores waiting for other trains, so it is a lower bound for a unit alone in the
  yard.
- `servicing_travel_allowance` in `train_unit_distribution` is a new, optional override (seconds).
  `check_config` no longer fills it in. If the location has no route to a needed facility, the
  generator falls back to 1800 s and logs a warning.
- Without servicing tasks nothing changes.

### Other

- `docker-push.sh` now logs out of ghcr.io when it exits.

### Why 2.3.0, not a patch

- Generated scenarios now carry `schemaVersion: 2`, and the package now depends on
  `robust-rail-general` `v0.2.0`.
- For configs with servicing tasks, departure times (and so the scenario for a given seed) differ
  from `2.2.0`, and generation can now fail for a time window that used to pass the
  sufficiency check. Configs without servicing tasks still generate the same scenarios for the same
  seed.
- The configuration file format is only extended (one new optional key), not changed.

### Verified via

- Full pytest suite: 66 tests, up from 55 at `2.2.0`.
- `ruff format --check`/`ruff check` clean.
- CI green on `main` at the merge of `#25`.

## 2.2.0 — 2026-09-21

The headline change is that in/outstanding trains are now allocated to parking tracks that
actually fit them; a cluster of bug fixes in random train generation, found while reviewing that
change, came along with it, plus internal test coverage for previously-untested generation control
flow.

### In/outstanding trains are now allocated to tracks that fit them (`#19`)

`assign_standing_tracks` used to be a plain `random.sample()` of parkable tracks paired against a
`random.sample()` of candidate trains, with no comparison between a composition's length and the
length of the track it landed on. Since in/outstanding trains are declared to sit on one specific
track as a single composition (unlike arriving/departing trains, which can't be split across
tracks either, but at least pass through a gateway first), this could generate a scenario asking to
park a 324m train on a 222m track — simply invalid. Tracks and candidates are now drawn together:
each candidate is checked against the tracks still free, and a composition that fits nowhere is
demoted back to an ordinary arriving/departing train instead of being forced onto a track too short
for it.

Alongside this: `units_per_composition` is now validated to be a non-empty list of positive whole
numbers, and any composition that ends up holding a unit of 6 or more carriages is capped at 2
units regardless of that setting, because longer combinations don't fit the tracks either
(compositions that only drew shorter units keep the size they were asked for).

### Bug fixes in random train generation, found during review

- `reset()` no longer clears `train_units_subtypes`. It's populated once from the loaded material
  before generation starts and isn't re-derived per attempt unless a `train_unit_types` sublist is
  configured, so clearing it meant a retry crashed with a `ZeroDivisionError` instead of
  regenerating — directly undermining the bounded-retry fix below.
- The generation retry loop is now bounded (`max_generation_attempts`, default 100) instead of
  looping forever on a config that can never produce a matching scenario, and it now actually
  catches `GenerationAttemptFailed` — a new internal exception meaning "this particular draw
  couldn't be completed, another attempt may well succeed" — instead of logging and continuing with
  a scenario that was never regenerated.
- Both the mixed-traffic and non-mixed-traffic arrival draws now raise `GenerationAttemptFailed`
  when there aren't enough gateway slots for the requested number of trains, instead of letting a
  raw `ValueError` crash the whole run.
- `average_servicing_time` is now computed for the custom-servicing-tasks path too, not just the
  default one. It previously stayed at 0 on that path, letting departure times be drawn without
  accounting for real servicing duration.
- `check_train_lengths`'s greedy track assignment now tries the longest train first instead of
  shortest-first. Pairing the longest train with the longest available track is the assignment that
  succeeds whenever any assignment of these trains to these tracks does; the old ascending order
  could pair the longest track with a train that didn't need it and then reject a scenario that
  actually fit.
- A train unit type missing from the length lookup now raises a clear error immediately instead of
  silently being treated as 0m long.

### Internal: test coverage for `main.py`'s generation control flow (`#21`, closes `#20`)

`create_scenario_from_config()` had no test coverage at all before this — it reads its config and
location from disk paths, so nothing in the suite built a fixture for it, and several of the bugs
above shipped without regression tests as a direct result. The bounded retry loop,
`average_servicing_time` calculation, and time-window-sufficiency check are now split into small,
independently-testable functions (`generate_random_trains`, `compute_average_servicing_time`,
`time_window_is_sufficient`), each with dedicated tests, and `create_trains()` (the
`trains_given: true` path) got test coverage for the first time as well. No behavior changed here —
this is coverage for logic that already existed.

### Why 2.2.0, not a patch

Generated output for the same seed and config is no longer guaranteed to match `2.1.0`: the
standing-track allocation rewrite and the retry/arrival-draw fixes both change how many random
draws happen and in what order, which changes the resulting scenario even for configs that don't
touch in/outstanding trains at all. The configuration file schema, CLI, and public functions are
unchanged — but the same-input-same-output guarantee the `2.1.0` notes could make doesn't hold here,
so this isn't a drop-in patch release.

### Verified via

- Full pytest suite: 55 tests, up from 17 at `2.1.0`.
- `scripts/regenerate_examples.py` re-run and its output confirmed fresh against what's checked
  into `data/`.
- `ruff format`/`ruff check` clean.
- CI green on both `#19` and `#21`.

## 2.1.0 — 2026-09-02

Two independent pieces of cleanup landed together: moving the interchange
models to `robust-rail-general`, and removing dead code left behind by
earlier migrations. Output is unchanged — every generated scenario JSON is
byte-identical to `2.0.0` for the same input, verified across the
trains-given and random-generation paths.

### Interchange models now come from `robust-rail-general`

The Pydantic models that define the wire format (`Location`, `Scenario`,
`Plan`) are no longer vendored in this repo. They're consumed as the
`robust_rail_models` package from `robust-rail-general` (pinned to `v0.1.1`)
instead (`robust-rail-generator#14`). `src/models/`, `schema/*.json`,
`scripts/export_schema.py`, and the CI job that kept the schema export fresh
are all gone — none of it was regenerable here anymore, so keeping it around
would only go stale silently.

**This is why the release is 2.1.0, not a patch:** anything importing
`models.scenario`/`models.location` directly from this package, or reading
its checked-in `schema/*.json` files, now breaks — and installing this
package pulls in `robust-rail-general` as a new git dependency. The wire
format itself is untouched (`schemaVersion` stays at `1`; see
`SCHEMA_CHANGELOG.md`), so this isn't a coordinated cross-repo schema bump
like `2.0.0` was — just this repo's own breaking change to its Python
surface and dependency graph, hence a minor rather than a major bump.

### `EvaluatorScenario` retired; dead code removed

`ScenarioGenerator` now builds `Scenario` directly instead of assembling the
deprecated flat `EvaluatorScenario`/`Train` shape and hand-converting it via
`create_solver_format_scenario()`. That conversion step and the
`SolverScenarioGenerator` class it fed are gone; `create_train()` splits into
`create_incoming_train()`/`create_train_request()`, each returning the real
`IncomingTrain`/`TrainRequest` types. (`robust-rail-generator#12`)

Alongside that, dead code found during an earlier audit was removed
(`robust-rail-generator#13`):

- Unused builders for staff/workers, non-service traffic, and disabled track
  parts. The `Scenario` fields and model classes stay — only the
  generator-side builders are gone. An enhancement issue
  (`robust-rail-generator#15`) was filed to reconsider adding these later.
- `RandomGenerator.resample_arrival_departure_times`, superseded by
  `assign_arrival_departure_times`.
- `check_matching`'s dead `minimal_yard_time` parameter — never wired to
  anything that used it.
- `ScenarioGenerator.load_scenario`, orphaned since `format_converter.py`
  (its last caller) was removed on 2026-08-03, unrelated to the
  `EvaluatorScenario` retirement above.

Verified via the full pytest suite (including new coverage for
`create_incoming_train`/`create_train_request`, standing-index propagation,
`check_matching`, and task propagation through in-standing trains) plus a
manual byte-for-byte diff of generator output against `2.0.0` across three
real configs.

## 2.0.0 — 2026-08-20

This is the generator's slice of the shared 2.0.0 release: the same interchange
format, tagged together, across `robust-rail-generator`, `robust-rail-solver`
(HIP) and `robust-rail-evaluator` (TORS). The full cross-repo picture —
verification evidence, what each repo changed, and the decisions behind the
schema — lives in `scenario-planning-inputs`' `docs/roadmap-2.0.0.md`.

### Protobuf is gone

The generator no longer reads or writes protobuf. Every model — `Location`,
`Scenario`, `Plan`, and the scenario-config format — is now a Pydantic model
under `src/models/`, and that package is the single source of truth for the
interchange format: JSON Schema is exported from it (`schema/*.json`, via
`scripts/export_schema.py`) rather than hand-maintained, and CI fails if the
checked-in schema drifts from the models. `env.yml`/conda are gone with it;
the project is `uv`-managed (`pyproject.toml`, `uv.lock`).

### Interchange format: breaking changes from the pre-2.0.0 shape

Anything reading generator output (or scenario-planning-inputs fixtures)
against the pre-migration shape needs to account for:

- **`displayName` → `typePrefix` + `carriages`.** A `TrainUnitType` is now
  identified by the pair, not a combined string like `"SLT4"`. `typePrefix`
  is the family name only (`"SLT"`, `"VIRM"`); `typeDisplayName` becomes a
  derived value, not a wire field.
- **`TaskSpec.priority` (int) → `TaskSpec.optional` (bool).** TORS only ever
  read `priority` as a zero/non-zero flag, so the field now says what it
  meant.
- **`Resource` is `{ "kind": "trackPart"|"facility"|"staff", "id": <int> }`.**
  Replaces three parallel `Optional[int]` fields; `name` is dropped.
- **Every ID is an `int`**, including composite ones. `trainUnitIds` (never
  produced or consumed by anything) is removed, and every remaining array of
  IDs is suffixed `IDs` (`memberIDs`, `parentIDs`, ...).
- **`Plan.trackParts` is dropped.** The evaluator loads infrastructure from
  `--path_location`; this field was always dead weight on the wire.
- **Enum wire values are PascalCase** (`"StandIn"`, not `"standIn"`), enforced
  at the schema level.
- **`standingIndex` is `Optional[NonNegativeInt]`**, required and mutually
  distinct within a group of `inStanding` trains sharing a track (a fact about
  the world at scenario start), optional within `outStanding` (a terminal
  requirement that may legitimately have no preferred order). Validated
  across sibling records on `Scenario`/`EvaluatorScenario`.
- **`trackParts`, `actions` and `trainUnitTypes` are now required**, not
  merely conventionally present — see `SCHEMA_CHANGELOG.md`'s "Unversioned —
  2026-08-12" entry for why this didn't need a `schemaVersion` bump.
- **`reversalDuration` and `canDepartFromAnyTrack` are dropped from the wire
  format entirely.** Traced every consumer first: the solver's real
  computation (`ShuntTrain.ReversalDuration`) derives it from `BackNormTime`
  + `Carriages * BackAdditionTime`; TORS's serializer hardcoded
  `canDepartFromAnyTrack` to `false` on output and never read it back; the
  solver's only former consumer of it (`Converter.cs`) was already gone.
  Zero behavioral effect anywhere. See `SCHEMA_CHANGELOG.md`'s
  "Unversioned — 2026-08-21" entry.

`schemaVersion: 1` is carried on `Location`, `Scenario`, and `Plan`; a
mismatch is a logged warning, never a hard reject (see `SCHEMA_CHANGELOG.md`).

### Known limitation: two canonical fixtures can't produce a valid plan

`6t_custom_example3` and `7t_custom_example1` — two of this repo's own
canonical KleineBinckhorst scenarios — are expected to fail downstream, not
because of anything in the generator, but because of open issues in the repos
that consume its output:

- `6t_custom_example3`: the solver parks on a non-parking arrival track when
  it can't move into the yard immediately (`solver#13`).
- `7t_custom_example1`: the solver's cost function has no deadline for
  outStanding trains, so it produces a plan that overruns the scenario
  horizon for free, which then trips a diagnostic-quality bug in the
  evaluator's terminal-state handling rather than a clean failure
  (`solver#14`, `evaluator#6`).

Both were deferred deliberately rather than blocking 2.0.0. If you're running
the full pipeline and see these two fail, this is why.

**Update, 2026-09-12:** solver/evaluator `2.1.0` (shipped 2026-09-11) fixes
solver#13 outright — `6t_custom_example3` now produces a valid plan.
`7t_custom_example1` needed more than solver#14 alone: the free-overrun and
the evaluator#6 spin it used to trip are both gone, but the scenario still
fails, now on a distinct, still-untriaged "departure mismatch" defect. See
`robust-rail-general`'s `docs/roadmap-2.0.0.md` for the investigation.

### Repo hygiene

- Generated scenario JSON (`save_scenario_json`) now always ends with a
  trailing newline, matching `scripts/export_schema.py`'s existing
  behavior. No content change, byte-only — every generated file's bytes
  differ as a result.
- `README.md`'s setup instructions now match reality (`uv sync`, `uv run`)
  instead of describing the conda-based world that predates `pyproject.toml`.
- `unified-schema-design.md` is marked historical — the migration it planned
  is this release.
- Linting and formatting (Ruff) are enforced via `pre-commit` and a CI job;
  see `.pre-commit-config.yaml` and `[tool.ruff]` in `pyproject.toml`.
- `src/generate-scenarios.sh` and the one-off `regression-baseline/` it fed
  are gone — both existed only to support the protobuf-to-Pydantic migration
  itself and have no role afterwards.

### Publishing

The generator image is versioned from `pyproject.toml`'s `[project] version`
and pushed to `ghcr.io/robust-rail-nl/generator` via `./docker-push.sh`
(multi-arch: `linux/amd64`, `linux/arm64`). The `generator:2.0.0` tag points
at the same image digest already verified as `2.0.0-rc.4` — re-tagged, not
rebuilt, so the tag names exactly the bytes that were tested. `:latest` moves
to `2.0.0` as the first stable tag of the release; it does not move for
`-rc.*`/`-beta.*` builds.

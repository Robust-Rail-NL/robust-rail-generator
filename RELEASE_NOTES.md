# Release notes

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

### Repo hygiene

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
at the same image digest already verified as `2.0.0-rc.2` — re-tagged, not
rebuilt, so the tag names exactly the bytes that were tested. `:latest` moves
to `2.0.0` as the first stable tag of the release; it does not move for
`-rc.*`/`-beta.*` builds.

# Generator refactor: protobuf → Pydantic

**Status: historical.** This refactor is complete — protobuf is fully removed
and the generator runs on the Pydantic models in `models/`. Kept as a record
of the original refactor plan; the "Key model notes" section below has been
updated to match the current schema (see `unified-schema-design.md` and
`SCHEMA_CHANGELOG.md` for what changed since).

## What this work is

Replace all protobuf usage in `robust-rail-generator` with native Pydantic
models. The generator currently reads and writes JSON via protobuf objects;
after the refactor it uses the Pydantic models in `models/` directly.

## The models

The `models/` package is the source of truth for the interchange format. It
contains:

| File | Contents |
|------|----------|
| `models/utilities.py` | `RailModel` (base class), `TimeInterval` |
| `models/location.py` | `Location`, `TrackPart`, `Facility`, `Resource`, `TaskType`, `PredefinedTaskType`, `WalkingDistanceEntry` |
| `models/scenario.py` | `Scenario`, `IncomingTrain`, `IncomingTrainUnit`, `TrainRequest`, `TrainUnit`, `TrainUnitType`, `ShuntingUnit`, `TaskSpec`, `MemberOfStaff`, `NonServiceTraffic`, `DisabledTrackPart` |
| `models/plan.py` | `Plan`, `Action` |

All models inherit from `RailModel`. Do not use `BaseModel` directly.

## Serialisation

Every model has two helper methods inherited from `RailModel`:

```python
obj.to_dict()   # → dict, camelCase keys, unset fields omitted
obj.to_json()   # → str, same conventions; accepts indent=2 for debug output
```

Always use these for output. Never call `model_dump()` or `model_dump_json()`
directly — they require `by_alias=True, exclude_unset=True` to produce correct
interchange JSON, and `to_dict()`/`to_json()` encapsulate that.

## Parsing

```python
location = Location.model_validate(data_dict)
scenario = Scenario.model_validate_json(json_string)
```

Pydantic accepts both `snake_case` and `camelCase` field names on input
(`populate_by_name=True` is set on `RailModel`). The generator's internal
code can use `snake_case`; wire format is `camelCase`.

## Wire format conventions

- Field names: `camelCase` in JSON, `snake_case` in Python.
- All times: seconds since the epoch, `int`.
- IDs: `int` (track parts, facilities, staff); `str` (trains, shunting units,
  train units).
- Enums serialise as strings: `"Move"`, `"StandIn"`, `"RailRoad"`, etc.
- Optional fields absent from input stay absent from output (`exclude_unset`).

## Key model notes

**`Scenario.in_`** — `in` is a Python keyword; the field is `in_` in Python
but serialises as `"in"` in JSON. Pydantic handles this transparently.

**`TrainUnitType` identity** — equality and hashing are by `(type_prefix,
carriages)`. `type_prefix` is the type family name only (`"SLT"`, `"SGM"`) —
it does NOT encode carriage count. Old code may use `"SLT4"` / `"SLT6"`;
replace with `type_prefix="SLT", carriages=4`. `type_display_name` is a
derived property (`type_prefix + "-" + carriages`), not a wire field.

**`TrainUnit.type_prefix` / `TrainUnit.carriages`** — the `(type_prefix,
carriages)` pair is the lookup key into `Scenario.train_unit_types`. Do not
embed the full `TrainUnitType` object in `TrainUnit`. `TrainUnit` also
exposes a derived `type_display_name` property for logging/bucketing.

**`ShuntingUnit.members`** — list of TrainUnit ID strings, not embedded
objects.

**`TaskSpec.optional`** — replaces the old `priority: int`. `False` means
the task must be completed before the train may exit the yard; `True` means
optional. Do not add `priority` back.

**`PredefinedTaskType`** enum values: `Move`, `Split`, `Combine`, `Wait`,
`Arrive`, `Exit`, `StandIn`, `StandOut`, `Walking`, `Break`, `NonService`.
`BeginMove` and `EndMove` are evaluator-internal and absent from the schema.

**`Plan.track_parts`** — acknowledged technical debt; kept for now because
the evaluator needs it. Do not remove it during this refactor.

## What to do with protobuf

- Replace all protobuf imports and generated-class usage with the Pydantic
  models above.
- Replace JSON-to-protobuf parsing with `Model.model_validate(...)`.
- Replace protobuf-to-JSON serialisation with `obj.to_dict()` / `obj.to_json()`.
- Once all usages are replaced, we can remove `env.yml` and the dependency on Anaconda,
  and delete the `.proto` files and any generated `_pb2.py` files from the
  generator project.

## Verifying correctness

Before starting, we have run the generator on a representative set of
scenarios (using `./generate-scenarios.sh`) and saved the JSON output as a
regression baseline under `./regression-baseline/'. After each module is
refactored, re-run and diff against the baseline. Expected differences:

- `displayName` field: old output may be `"SLT4"`; new output is `"SLT"` with
  `"carriages": 4`. This is an intentional breaking change — coordinate with
  the solver before merging.
- Fields that were always protobuf defaults (e.g. `priority: 1`, empty
  `standingType`) will be absent from new output. This is correct.
- Everything else should be semantically identical.

## Open questions (do not resolve during this refactor)

These are noted in the models as `TODO` comments. Leave them as-is:

- Is `reversalDuration` computed from `backNormTime`/`backAdditionTime` or
  separate?
- Is `travelSpeed` per-type or per-location?
- Should `canDepartFromAnyTrack` be on `TrainRequest`?
- Should `standingIndex` be on `IncomingTrain` as well as `TrainRequest`?
- Should `Action.shunting_unit` be an ID reference rather than an embedded
  object?
- Are the three movement coefficients on `Location` per-location or global?

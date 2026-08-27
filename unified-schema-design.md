# Unified Schema Design

Design record for the migration away from Protobuf to a single Pydantic-defined
schema consumed by all three projects (generator, solver, evaluator).

**Status: historical.** The migration this document planned is complete: the
schema is frozen and implemented across all five Robust-Rail-NL repos, shipped
as part of the 2.0.0 release (see `../robust-rail-general/docs/roadmap-2.0.0.md`
for the release record). Kept as a record of *why* the schema looks the way it
does — most "Decision" entries below are still accurate descriptions of the
shipped models. A handful of "Open question" entries were never closed out
before the freeze; those are called out as such rather than removed, since the
underlying ambiguity in the code is real (see each for the corresponding TODO,
if any). None of them blocks 2.0.0.

## Guiding principles

1. **Pydantic is the source of truth.** Models live in the generator (Python).
   JSON Schema is exported from these models and is the artifact the solver and
   evaluator consume / validate against.
2. **One unified model, not per-consumer variants.** Fields only some consumers
   care about are `Optional` and may be ignored by others. Where the two existing
   protobuf models genuinely disagree about the *shape* of a concept (not just
   what fields are present), we pick one shape and adapt the others.
3. **Prefer the more honest model over the more compact one.** Where the existing
   schemas have compressed distinct concepts into a single shape, we uncompress.
   (Concrete example: `Train` below.)
4. **Strict validation by default.** `extra="forbid"`; no implicit type coercion.
   Forward compatibility for the addition of new optional fields is handled by
   bumping a schema version and allowing consumers to opt into laxer reads if
   needed. (Open question — see end.)

## Decisions per concept

For each top-level concept: the unified shape, what's required vs optional, which
consumer needs each optional field, and open questions.

### `Location`

Mostly additive between the two proto models. Unified shape: HIP shape extended
with the evaluator/generator-specific fields, all optional.

- **Required for all consumers:** `trackParts`, `facilities`, `taskTypes`.
- **Required for generator/evaluator, optional for solver:**
  `movementConstant`, `movementTrackCoefficient`, `movementSwitchCoefficient`,
  `distanceEntries` (walking distance matrix). The solver currently doesn't see
  these; the evaluator uses them for shunting time and walking distance
  calculations.

**Open question, unresolved at freeze:** are the three movement coefficients
(`movementConstant`, `movementTrackCoefficient`, `movementSwitchCoefficient`)
truly per-`Location` or are they actually global constants that happen to be
transported via the Location message? Shipped as per-`Location` fields for
2.0.0 either way; revisit if a second location's values are ever observed to
differ from the first, which would settle it empirically.

### `TrackPart`

Additive. Unified shape: HIP shape plus evaluator-specific fields.

- **Required for all:** `id`, `type`, `aSide`, `bSide`, `length`, `name`,
  `sawMovementAllowed`, `parkingAllowed`.
- **Optional (evaluator/generator only):** `isElectrified`, `stationPlatform`.
- **Enum `TrackPartType`:** unified set. The non-HIP version has `Building`
  with the note "Do not add trackparts with this type when sending to HIP."
  Under unification this comment goes away — `Building` is just a valid value
  the solver doesn't care about but won't choke on. `HalfEnglishSwitch` is
  marked deprecated in the non-HIP version but still present in HIP. Keep it
  for now; mark deprecated in the unified model.

### `Facility`

Additive.

- **Required for all:** `id`, `type`, `relatedTrackParts`, `taskTypes`,
  `simultaneousUsageCount`.
- **Optional (evaluator/generator only):** `timeWindow`.

### `Resource`

Unified to include the `staffId` variant (from the non-HIP version). The
solver simply won't encounter `staffId` resources in practice.

**Decision: introduce an explicit `kind` discriminator field.**

Wire shape (schemaVersion 1):

```json
{ "kind": "trackPart", "id": 57 }
{ "kind": "facility",  "id": 72 }
{ "kind": "staff",     "id": 5  }
```

The `name` field (previously a redundant string copy of the numeric ID) is
dropped. The `staffId` variant is kept in the schema; the solver will never
produce it but must not choke on it in input.

**Per-consumer changes:**

- ~~**Generator (Python/Pydantic):** replace the three `Optional[int]` fields and
  the `@model_validator` with `kind: Literal["trackPart", "facility", "staff"]`
  and `id: int`.~~ **Done** (`16dc053`) — used a `ResourceKind` str enum rather
  than a bare `Literal`, for consistency with `TrackPartType`/`PredefinedTaskType`
  elsewhere in this file; behaviour is the same.
- **Solver (C#, `noproto` branch):** `NoProto/Location.cs` — update the
  `Resource` record to `(string Kind, ulong Id)` and the two factory methods
  (`FromInfra`, `FromFacility`). `PlanGraph.cs` needs no changes (all
  construction goes through the factories).
- **Evaluator (C++, `noproto` branch):** update `protos/HIP_Location.proto`
  (replace `oneof { trackPartId, facilityId }` with `string kind` + `uint64 id`);
  update the two access sites in `Plan.cpp` to dispatch on `resource.kind()`.
  Add a hard error (`throw`) for any unrecognised `kind` value, so that an
  old-format plan produces an immediate, informative failure rather than a
  silently wrong result. (The schemaVersion warning fires first; the `kind`
  check is a belt-and-suspenders guard.)

### `TaskType`

Identical structure in both protos (a oneof of `predefined` or `other`).
Unify the `PredefinedTaskType` enum to the larger set (non-HIP):
`Move`, `Split`, `Combine`, `Wait`, `Arrive`, `Exit`, `Walking`, `Break`,
`NonService`, `BeginMove`, `EndMove`. Solver consumers will only encounter
the smaller subset in practice.

**Decision: `BeginMove` and `EndMove` are not interchange concepts.** They
are used internally by the evaluator but are never provided as input from
the generator or solver. They do not belong in the unified schema or the
exported JSON Schema. The C++ evaluator should define them locally — either
as an extension of the interchange enum or as a separate internal type that
the interchange enum maps into on ingestion.

**Decision: `StandIn` and `StandOut` are interchange concepts and belong in
the unified schema.** They appear in `Plan` actions as the standing-train
equivalents of `Arrive` and `Exit` respectively — used for trains that were
already present in the shunting yard at scenario start (`StandIn`) or will
remain after scenario end (`StandOut`). They are produced by the solver and
consumed by the evaluator.

The `PredefinedTaskType` enum in the Pydantic model is therefore:
`Move`, `Split`, `Combine`, `Wait`, `Arrive`, `Exit`, `Walking`, `Break`,
`NonService`, `StandIn`, `StandOut`.

**Decision: wire format is always PascalCase for enum values, and this is
enforced at the schema level.**

- `"Break"`, `"StandIn"`, `"Move"` — not `"break"`, `"standIn"`, `"move"`.
- **Pydantic** defines enum members with PascalCase string values
  (`Move = "Move"`, not `Move = "move"`); validation therefore rejects
  non-PascalCase input without any extra logic.
- **Solver (C#)** must be fixed to emit PascalCase. The `JsonStringEnumConverter`
  in `System.Text.Json` uses the C# member name (already PascalCase) by
  default — if lowercase is currently being emitted, it is due to a custom
  naming policy or a protobuf JSON holdover and is a targeted fix.
- **Evaluator (C++)** drops the lowercase proto aliases once the solver is
  fixed; no tolerance layer needed in steady state. The `break` C++ keyword
  collision (blocking a lowercase alias for `Break`) is a non-issue:
  `"Break"` is the canonical spelling.
- Solver and evaluator changes are made simultaneously so integration is
  never in a state where one side is strict and the other isn't.
- Existing plan files with lowercase task-type values become invalid. This
  is acceptable at pre-release (no stable 2.0.0 yet).

**C# note.** The C# `PredefinedTaskType` enum currently has only
`Move`, `Split`, `Combine`, `Wait`, `Arrive`, `Exit` — it needs `Walking`,
`Break`, `NonService`, `StandIn`, and `StandOut` added. The commented-out
`StandOut = 6` and `StandIn = 7` entries can now be uncommented and
renumbered (or left at 6 and 7 if the numeric values don't matter for the
JSON interchange). Worth verifying whether `Walking`, `Break`, and
`NonService` are ever present in JSON the solver reads, and that the
deserializer handles them gracefully once the enum is extended.

### `TrainUnitType`

This is the messiest of the additive cases because there's a semantic question
mixed in.

- **Required for all:** `displayName`, `carriages`, `length`, `combineDuration`,
  `splitDuration`, `backNormTime`, `backAdditionTime`.
- **Optional (generator/evaluator only):** `travelSpeed`, `startUpTime`,
  `typePrefix`, `needsLoco`, `isLoco`, `needsElectricity`, `idPrefix`.

**Decision: `TrainUnitType` is identified by `typePrefix` + `carriages`; `displayName` is dropped as a wire field.**

- `typePrefix` is the type *family* name: `"SLT"`, `"VIRM"`, `"SNG"`, `"FFF"`.
  It is already present on `TrainUnitType` in the C# record and in
  `default_train_unit_types.json` with this exact semantics.
- `carriages` is the carriage count: `4`, `6`. Already a separate field.
- `typeDisplayName` is a **derived value** — `typePrefix + "-" + carriages`
  (e.g. `"SLT-4"`, `"VIRM-6"`) — computed on demand, not stored on the wire.
  It is useful for display and logging but is not part of the schema.
- Consumers that need a unique type key use `(typePrefix, carriages)`.
  The C# `Equals`/`GetHashCode` currently key on `(DisplayName, Carriages)`;
  once the rename lands, they key on `(TypePrefix, Carriages)` instead.

**Per-consumer changes:**

- **Generator**: rename `display_name` → `type_prefix` in `TrainUnitType`
  Pydantic model and all call sites. Strip the carriage suffix from config
  `name` values when assigning `type_prefix` (e.g. `"SLT-4"` → `"SLT"`).
  Fix `add_custom_train_unit_types` to read `unit_type["typePrefix"]`
  (camelCase, matching the JSON) — the current `unit_type.get("type_prefix", None)`
  is wrong and silently drops the field.
- **HIP (C#)**: rename `DisplayName` → `TypePrefix` on `TrainUnitType`;
  update `Equals`/`GetHashCode` accordingly. Remove any code path that
  concatenates type name and carriage count. `ProblemInstance.cs`'s
  `traintypemap` must key on `(TypePrefix, Carriages)` — the current
  `traintypemap[unit.TypeDisplayName]` lookup breaks once two variants
  share the same family name.
- **TORS (C++)**: update any type lookup that matches on `displayName`
  alone to match on `(typePrefix, carriages)`.

**Config cleanup (this repo):** `scenario_config_test.json` has wrong
`typePrefix` values — they embed the carriage count (`"SLT4"`, `"VIRM4"`)
rather than the family name (`"SLT"`, `"VIRM"`). Fix to match
`default_train_unit_types.json`.

**Config cleanup (this repo):** `scenario_config_test.json` conflated train unit
*instances* (NS fleet IDs like `"SLT4-4"`, `"SLT5-5"`) with train unit *types*.
These have been collapsed to the 18 distinct real types (`"SLT-4"`, `"SLT-6"`,
`"VIRM-4"`, etc.) that the config was actually modelling.

**Decision: `reversalDuration` is computed from `backNormTime` and
`backAdditionTime` and is dropped from the wire format.** The solver derives
it locally; it does not appear in the unified schema.

**C# notes.**

- The C# `TrainUnitType` overrides `Equals` and `GetHashCode` to key on
  `(DisplayName, Carriages)`. This implicitly endorses the proposed cleanup
  of the `displayName` overloading — identity is type + count, not the
  concatenated string. Good signal that the direction is right; the
  remaining work is making the wire format match.
- The C# code's `ShuntTrain.ReversalDuration` is a computed property (sum of
  `VariableReversalDuration` across units plus the first unit's
  `BaseReversalDuration`), and those in turn are populated straight from
  `BackNormTime`/`BackAdditionTime` when building `TrainType`s
  (`ProblemInstance.cs`). The standalone `ReversalDuration` field that used to
  sit on the interchange DTO (`Interchange/Scenario.cs`) was never read
  anywhere and has been removed — confirming the decision above.

### `Scenario` and the train shapes — the structural divergence

This is the place where the two existing models genuinely disagree about the
domain, not just about which fields are present. **Decision: adopt the HIP
shape**, with extensions.

Rationale: the non-HIP `Train` is overloaded — its `time` field means
arrival-time, departure-time, or zero (= standing) depending on context, and
its `parkingTrackPart`/`sideTrackPart` semantics flip depending on whether the
train is incoming or outgoing. The HIP model splits these honestly:

- `IncomingTrain` for arriving trains and standing-in trains
- `TrainRequest` for departing trains and standing-out trains
- Four separate sections in `Scenario`: `in`, `inStanding`, `out`, `outStanding`

The unified `Scenario` looks like:

```
Scenario:
  in:          list[IncomingTrain]
  inStanding:  list[IncomingTrain]
  out:         list[TrainRequest]
  outStanding: list[TrainRequest]
  nonServiceTraffic: list[NonServiceTraffic]    # optional, generator/evaluator
  disabledTrackParts: list[DisabledTrackPart]   # optional, generator/evaluator
  workers:     list[MemberOfStaff]              # optional, generator/evaluator
  startTime:   int
  endTime:     int
  trainUnitTypes: list[TrainUnitType]           # was on Scenario in non-HIP only
```

**Resolved:** `trainUnitTypes` stays on `Scenario`, referenced by name from
`TrainUnit` — see the "Settled — decisions still in force" table in the
roadmap.

**Decision: `standingIndex` appears on both `IncomingTrain` and
`TrainRequest`.** TORS reads it for both incoming standing and outgoing
standing trains. The proto field is already field 7 on each in the evaluator's
local `HIP_Scenario.proto`; generator and design doc should match.

**Type and required-ness are settled below** — see "Standing order
(`inStanding` / `outStanding`)" after the `IncomingTrain` / `TrainRequest`
section.

**Open question, unresolved at freeze:** `minimumDuration` (non-HIP) landed on
the shipped `Train` model as `Optional[str]` without its meaning being pinned
down — no consumer reads it yet.

### `IncomingTrain` / `TrainRequest`

`IncomingTrain` unified:
- `entryTrackPart`: where it arrives over (was `sideTrackPart` in non-HIP)
- `firstParkingTrackPart`: where it ends up (was `parkingTrackPart` in non-HIP)
- `arrival`: arrival time
- `departure`: time it leaves (often equals scenario end for standing trains)
- `id`
- `members`: list of `TrainUnit` (with embedded tasks — see `TrainUnit` below)

`TrainRequest` unified:
- `leaveTrackPart`
- `lastParkingTrackPart`
- `arrival` / `departure`
- `displayName`
- `trainUnits`: list of `TrainUnit` (optionally with unspecified IDs to mean
  "any train unit of this type")
- `standingIndex`

**Resolved: `canDepartFromAnyTrack` is dropped from the wire format.** The
non-HIP `Train` shipped it (for outstanding trains) as `Optional[bool]`; HIP
has no equivalent. Traced every consumer: the generator only ever wrote it,
TORS's C++ serializer hardcoded `false` on output regardless of the input
value and never read it back for any decision, and the solver's only former
consumer (`Converter.cs`) had already been deleted. Zero behavioral effect
anywhere, so it's removed rather than kept as dead weight.

### Standing order (`inStanding` / `outStanding`)

**Decision: `standingIndex` is `Optional[NonNegativeInt]` on both
`IncomingTrain` and `TrainRequest`, required (and mutually distinct) within
`inStanding` groups sharing a track, left optional within `outStanding`.**

- **Type.** Neither engine ever does arithmetic with this value — both only
  compare it to establish an order (`ExitAction.cpp`'s `minIndex` scan,
  `ArriveAction.cpp`'s tie check). cTORS's own `TrainGoal` already types it
  `const int` internally (`TrainGoals.h:23`) and truncates the wire's
  `double` down to that at construction (`TrainGoal.cpp:41`); no fractional
  value appears anywhere in the current corpus either. The `double` never
  bought real precision, so it becomes `NonNegativeInt` — negative values
  have no interpretation.

- **Required within `inStanding`.** Which unit sits at which end of a track
  is a fact about the world at scenario start, the same kind of given as
  `entryTrackPart` for an arriving train — leaving it unconstrained doesn't
  add flexibility, it under-specifies the scenario: two solvers (or two runs
  of one solver) can each produce a plan valid for a different starting
  arrangement while nominally solving "the same scenario." `solver#17`
  already shows this failure mode in practice (solver and evaluator
  disagreeing which side a combined inStanding unit's members sit on);
  `solver#18` is the same defect for order — the field is parsed and then
  never read again, so ordering silently falls back to solver-internal
  arrival order instead of the scenario's own statement. Enforced as a
  validation rule across sibling records sharing a track, not by the field's
  own type — a track with a single standing unit has nothing to be ordered
  against, so the rule only bites where ambiguity is actually possible.

- **Optional within `outStanding`.** Unlike inStanding, outStanding order
  describes a terminal requirement, not a given fact — "park these N units
  on this track by the end of the horizon, no preference on order" is a
  complete, valid specification, not a data gap. `null` means exactly that.
  A scenario that does care can still set distinct indices, using the same
  field and comparison semantics as `inStanding`.

### `TrainUnit`

Two questions intertwined: (a) does `TrainUnit` carry tasks, and (b) does it
embed the `TrainUnitType` or reference it by name?

**Tasks.** The non-HIP `TrainUnit` has `tasks` directly. The HIP version wraps
this: there's a `TrainUnit` with no tasks, and an `IncomingTrainUnit` that
wraps a `TrainUnit` with tasks. The wrapper exists because outgoing trains
(in `TrainRequest`) don't have task lists. **Decision: tasks live on
`IncomingTrain.members[*]`** as a separate `IncomingTrainUnit` (or equivalent
nested model), not on `TrainUnit` itself. `TrainRequest.trainUnits` is plain
`TrainUnit`. This matches the HIP shape and is more honest.

**Type reference.** Non-HIP `TrainUnit` has `typeDisplayName` (a string
reference). HIP `TrainUnit` has `type` (an embedded `TrainUnitType` object).
**Decision: reference by `(typePrefix, carriages)` pair** — `TrainUnit`
carries both `typePrefix: str` and `carriages: int`, forming the lookup key
into `Scenario.trainUnitTypes`. `typeDisplayName` is a derived value
(`typePrefix + "-" + carriages`) and does not appear on the wire. A bare
string reference is insufficient because a single type family (e.g. `"SLT"`)
can appear with multiple carriage counts; embedding the full type object is
redundant and risks inconsistency.

**C# note.** The C# `TrainUnit` currently has *both* `Type` (embedded object)
*and* `TypeDisplayName` (string). This is a mid-migration state, not an
endorsement of keeping both. The Pydantic model should commit to
`typeDisplayName` only; the C# code can drop `Type` once the wire format is
fixed.

### `ShuntingUnit`

The two models disagree on `members`:
- Non-HIP: `repeated string` (IDs)
- HIP: `repeated TrainUnit` (embedded)

**Decision: IDs.** Same reasoning as `TrainUnit.type` — reference, don't embed.
Consumers that need the full `TrainUnit` look it up via the scenario.

**Decision: `standingType` is dropped.** It was added for communicating
standing-train status to the evaluator but was never actually used. Under
the unified model it is also fully redundant: `StandIn`/`StandOut` task
types in `Plan` actions carry that information explicitly. Already removed
from the C# code.



### `TaskSpec`

Unified shape:
- `type`: `TaskType`
- `duration`: int
- `requiredSkills`: list[str] — optional/empty for solver
- `optional`: bool, default `false` — replaces `priority` (see below)

**Note: `requiredSkills` is present in the unified spec above and is actively
read by TORS.** The HIP-shaped `TaskSpec` message in `HIP_Scenario.proto` is
missing it — not a design question, just an implementation gap the evaluator's
proto update must close.

**Decision: replace `priority: int` with `optional: bool`.**

The TORS evaluator uses `priority` only as a binary flag — `0` means the task
must be completed before a train may exit the yard; any non-zero value means
optional. The two rule files that implement this (`mandatory_service_task_rule.cpp`
and `optional_service_task_rule.cpp`) both reduce to a single zero/non-zero check.
No code anywhere in cTORS, pyTORS, or the Python TORS layer distinguishes between
different non-zero values. The proto comments are contradictory (`Scenario.proto`
says lower = more important; `HIP_Scenario.proto` says higher = more important and
marks the field `deprecated = true`); neither interpretation is implemented.

Wire-format mapping:
- `"priority": 0` → `"optional": false`
- `"priority": <non-zero>` → `"optional": true`

**Per-consumer changes:**
- **Generator**: field renamed to `optional: bool = False` in Pydantic model;
  field may be omitted on the wire when `false`; `data/default_servicing_tasks.json`
  updated (all non-zero values → `true`).
- **TORS**: `Task::priority` (int) renamed to `Task::optional` (bool), defaulting
  to `false` when absent; rule files simplified to check `!task.optional` / `task.optional`.
- **HIP**: field was already deprecated and unused — drop from deserialization entirely.

### `MemberOfStaff`

Present in non-HIP `Scenario` only. Unified: keep the full non-HIP shape, make
the whole `workers` field optional at the `Scenario` level.

Fields: `id`, `type`, `skills`, `shifts`, `breakWindows`, `breakDuration`,
`startLocationId`, `endLocationId`, `canMoveTrains`, `name`, `breakLocationId`.

### `NonServiceTraffic` and `DisabledTrackPart`

Present in non-HIP only. Keep as-is, optional at the `Scenario` level.

Note: the non-HIP proto comment for `DisabledTrackPart` calls it "An incoming
magic train" and references "fetching wizards." This is clearly stale
commentary from the original undergrad team. Replace with an actual
description of what the message represents.

### `TimeInterval`

Utility type, carries over unchanged.

### `SolverBackend`

**Dropped.** Not read, written, or used anywhere. Absent from the unified
schema and from the Pydantic models.

### `Plan` and `Action` — the solver's output

The document so far covers *input* to the solver and evaluator. The solver
also produces a `Plan`, which the evaluator consumes. Surfaced from the C#
code (no proto for this was shared); details are tentative.

A `Plan` is a list of `Action`s plus, currently, a list of `TrackPart`s. An
`Action` has a time interval, a task type, a `ShuntingUnit`, a primary
location (TrackPart ID), additional `Resource`s involved, and an optional
list of train unit IDs participating.

Several things worth deciding for the unified model:

- **`Plan` lives in its own schema file** (`plan.py`) — already the case in
  the current implementation. No change needed.
- **`Plan.trackParts` is dropped.** The C# comment reads "This field should
  be temporary and be replaced as soon as we send input to the algorithm."
  Confirmed: TORS never reads `Plan.trackParts` — it loads all infrastructure
  from `--path_location` via `LocationEngine`. The field is dead weight on
  the wire. HIP should stop emitting it; it is absent from the unified schema.
- **`Action.shuntingUnit` embeds a full `ShuntingUnit`** rather than
  referencing by ID. This is inconsistent with the "reference, don't embed"
  direction the rest of the document argues for. **Unresolved at freeze** —
  shipped embedded; switching to ID reference is cleaner but requires the
  evaluator to have access to the same `ShuntingUnit` registry the solver
  used.

Both remaining open questions below are moot now that protobuf is gone
entirely: there is no proto file for `Plan`, canonical or otherwise, and the
plain-vs-assert pipeline re-verification recorded in the roadmap (rc.1 and
later) confirms the evaluator parses and executes what the solver emits.

## C# reconciliation notes

The C# records are mid-migration. They contain several "keep both shapes
while figuring it out" patterns that are reasonable for a code base
transitioning piecewise, but that the Pydantic model — being the source of
truth — needs to commit on.

Places where C# is holding two shapes that the unified schema should
collapse to one:

- `TrainUnit.Type` (embedded `TrainUnitType`) vs. `TrainUnit.TypeDisplayName`
  (string reference). Unified: keep `typeDisplayName`, drop `type`.
- `ShuntingUnit.Members` (embedded `IList<TrainUnit>`) vs.
  `ShuntingUnit.MemberIDs` (`IList<string>`). Unified: keep `memberIDs`,
  drop `members`.
- `TaskSpec.Priority` carried with a TODO comment. Unified: dropped.
- `ShuntingUnit.StandingType`: dropped. Already removed from C# code.

Places where C# has narrower coverage than the unified schema needs:

- `PredefinedTaskType` enum only contains the HIP subset. The unified enum
  is larger; the C# enum will need to grow, or the solver needs a tolerant
  "unknown task type" path.
- `Resource` lacks the `staffId` variant. The unified `Resource` includes
  it; C# can omit it from its own model (the solver doesn't need it) so
  long as the JSON deserializer tolerates the variant being present in
  input it ignores.
- `MemberOfStaff` in C# is a partial shape (only a subset of fields). The
  unified shape is the full non-HIP one. Same tolerance argument as
  `Resource` — C# can keep its narrower view.
- `Location` in C# omits movement coefficients, walking distances, and
  several `TrackPart`/`Facility` fields. Same pattern: unified model is a
  superset, C# reads what it needs.

The asymmetry is worth being explicit about: **the C# model can legitimately
be narrower than the unified schema, but it cannot be inconsistent with it**.
"Field present but absent from C# model" is fine. "Field present in C# with
different semantics" is not.

Things the C# code reveals that aren't strictly schema concerns but matter
for the migration:

- **Hashability is mixed.** Some records are hashable, some explicitly are
  not (see `UnhashableRecord`, `Plan`). The Pydantic model will face the
  same tension: `frozen=True` makes models hashable but requires all
  contents to be hashable. Worth being deliberate about which models need
  equality, which need hashing, and which need neither. (See cross-cutting
  questions below.)
- **`EvaluatorScenario` is the legacy non-HIP shape kept around in C#.**
  Naming suggests you already see it as transitional. The unified migration
  is the moment to retire it on the evaluator side too — but only once the
  C++ evaluator can read the unified shape.



1. **Schema versioning.** **Decision:** `schemaVersion` is an independent
   monotonic integer (starting at `1` for the 2.0.0 release, incrementing only
   on breaking schema changes). It appears at the top level of `Location`,
   `Scenario`, and `Plan` — one shared interchange version across all three.
   Each tool defines a local constant `EXPECTED_SCHEMA_VERSION = 1`; all three
   are updated together as part of a coordinated release when the version bumps.
   A `SCHEMA_CHANGELOG.md` in this repo records what changed at each increment.

2. **Forward compatibility policy.** **Decision:** warn-and-continue. If
   `schemaVersion` is missing or differs from the expected value, the consumer
   logs a warning and proceeds. No hard reject on version mismatch, and no
   tiered compatibility matrix. This can be tightened later if long-lived
   deployments require it.

3. **Field naming conventions.** Proto uses `camelCase`. C# records presumably
   use `PascalCase` (with JSON attributes). Python convention is `snake_case`.
   Pydantic can handle aliases (`Field(alias="camelCase")`). The wire format
   should stay `camelCase` for compatibility with existing JSON; Python code
   uses `snake_case` internally.

4. **What about ID types?** Proto uses `uint64` for various IDs. JSON has only
   one number type and a string type. JavaScript and some JSON parsers can't
   handle uint64 cleanly.

   **Decision: plain JSON numbers, not quoted strings.** The generator's
   Pydantic models already emit raw numbers (`"arrival": 600`, not `"600"`).
   HIP's JSON writer previously quoted all numeric fields
   (`JsonNumberHandling.WriteAsString` in `Extensions.cs`) as a holdover
   from protobuf's JSON mapping, which quotes 64-bit fields specifically to
   protect JS/double-based JSON consumers from precision loss. That's been
   dropped: TORS's protobuf-based JSON reader accepts both quoted and
   unquoted 64-bit numbers on read (the spec only requires quoting on
   write), and no current ID or timestamp value approaches the 2^53 safe-
   integer boundary where this would matter. Revisit if a field ever
   genuinely needs the full 64-bit range and a double-based consumer (e.g.
   a JS/web tool) enters the pipeline.

5. **Schema location and distribution.** Where does the exported JSON Schema
   live? Checked into each project, or published as an artifact (npm package /
   NuGet / a tagged GitHub release)? This affects how the C# and C++ projects
   pick up changes. **Shipped for 2.0.0 as checked-in `schema/*.json`, read by
   `validate-fixtures.yml` off the branch named `release/2.0.0`.** Still
   genuinely open long-term — see "Where the exported schemas should live" in
   the roadmap for the known problem with the branch-name approach and the
   proposed fix (publish keyed by `schemaVersion`).

6. **Hashability and equality.** Pydantic v2 makes models hashable only with
   `frozen=True` and only if all contents are hashable (no `list`s, etc.).
   The C# code reveals an existing tension: some types are hashable, some
   throw on `GetHashCode` (`UnhashableRecord` is the base for `Plan`).
   `Action` overrides `Equals`/`GetHashCode` to consider only non-list
   fields. Worth deciding per-model: which need equality (value-based
   comparison), which need hashing (use in sets/dict keys), which need
   neither. As a starting heuristic: leaf value types (`TimeInterval`,
   `TrainUnitType` identity, `TaskType`) want both; collection-holding
   container types (`Plan`, `Scenario`, `Location`) want neither.
   **Resolved by default, not by decision:** no Pydantic model in
   `src/models/` sets `frozen=True`, so nothing is hashable. `TrainUnitType`
   gets its `(typePrefix, carriages)` identity via explicit `__eq__`/`__hash__`
   overrides instead of `frozen=True` (see `CLAUDE_CODE_CONTEXT.md`). No other
   model has needed equality or hashing so far.

## What actually happened

The numbered plan this section used to lay out (reconcile with C#, draft the
Pydantic models, generate JSON Schema, cut the generator over, coordinate the
breaking changes with C# and C++, move on to the evaluator) is done — that is
what shipped as the 2.0.0 interchange schema. For the detailed, dated account
of how the migration actually went (including the parts that didn't go
according to this plan), see `git log -p unified-schema-design.md` and the
roadmap's "Settled — what was done" section.

## Open questions still unresolved at freeze

Everything scattered through the document above that shipped without being
pinned down, gathered here for convenience. None of these blocked 2.0.0; they
are latent ambiguity in the shipped schema, not missing features.

- Are the three `Location` movement coefficients per-location or actually
  global constants?
- Are `Walking`, `Break`, `NonService` task types ever present in JSON the
  solver reads? If so, verify the C# deserializer handles them gracefully.
- What does `Train.minimumDuration` (non-HIP) mean? Shipped as
  `Optional[str]`; no consumer reads it.
- Should `Action.shuntingUnit` reference a `ShuntingUnit` by ID instead of
  embedding it? Shipped embedded.
- Where should the exported schemas live long-term? See "Where the exported
  schemas should live" in the roadmap.

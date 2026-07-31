# Unified Schema Design

Working document for the migration away from Protobuf to a single Pydantic-defined
schema consumed by all three projects (generator, solver, evaluator).

**Status:** Draft, derived from the existing `.proto` files and reconciled
against the in-progress C# records. Several decisions remain open; see the
"C# reconciliation notes" section and the per-concept open questions.

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

**Open question:** are the three movement coefficients (`movementConstant`,
`movementTrackCoefficient`, `movementSwitchCoefficient`) truly per-`Location`
or are they actually global constants that happen to be transported via the
Location message? If global, they belong somewhere else.

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

**Decision: keep the current wire format for now.** Three candidate approaches
exist; the decision is deferred until the evaluator migration to minimise
wire format changes:

- *Current shape: nullable fields with validator.* Three optional fields
  (`trackPartId`, `facilityId`, `staffId`), exactly one set, enforced by a
  Pydantic `model_validator`. Preserves the existing wire format exactly.
  Mildly awkward to express but no changes required for any consumer.

- *Explicit discriminator field.* Add `kind: "trackPart" | "facility" |
  "staff"` plus a single shared `id` field. Cleaner schema and unambiguous
  parsing, but changes the wire format for all three consumers. Best deferred
  to a coordinated update.

- *Inheritance.* A base `Resource` with `name`, and subclasses
  `TrackPartResource`, `FacilityResource`, `StaffResource` each with their
  own required `id` field. Usage sites annotated as
  `list[TrackPartResource | FacilityResource | StaffResource]` (not
  `list[Resource]`, which would cause serialisation to truncate to base
  class fields). Can preserve the existing wire format if no discriminator
  field is added, but Pydantic's parsing becomes order-sensitive without one.

The nullable-fields-with-validator shape is the current implementation.
Revisit when migrating the evaluator.

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

**Decision: fix the `displayName` overloading.** The current non-HIP proto has a
`#warning` comment noting that `displayName` is "currently 'SLT4' or 'SLT6'"
rather than just 'SLT'. Under the unified model:

- `displayName` is the train *type* name only: "SLT", "SGM", "VIRM".
- `carriages` carries the carriage count: 4, 6.
- `typePrefix` (if needed at all) is redundant with `displayName` and could be
  removed.

This is a behavior change in the generator output and requires coordinated
updates. Worth confirming.

**Decision: `reversalDuration` is computed from `backNormTime` and
`backAdditionTime` and is dropped from the wire format.** The solver derives
it locally; it does not appear in the unified schema.

**C# notes.**

- The C# `TrainUnitType` overrides `Equals` and `GetHashCode` to key on
  `(DisplayName, Carriages)`. This implicitly endorses the proposed cleanup
  of the `displayName` overloading — identity is type + count, not the
  concatenated string. Good signal that the direction is right; the
  remaining work is making the wire format match.
- The C# code keeps both `ReversalDuration` *and* `BackNormTime`/`BackAdditionTime`
  as fields. Doesn't tell us whether `reversalDuration` is computed or separate,
  but does mean the question is still open in code, not just on paper.

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

**Open question:** where does `trainUnitTypes` belong? The non-HIP `Scenario`
has it; the HIP `Scenario` does not (HIP embeds `TrainUnitType` directly
inside `TrainUnit`). Putting it on `Scenario` and referring to it by name from
`TrainUnit` is more normalized. Confirm that's the right call.

**Open question:** the non-HIP `Train` has a `standingIndex` field and a
`minimumDuration` field. `standingIndex` exists in HIP `TrainRequest` but not
`IncomingTrain`. Should `standingIndex` be on both? Where does
`minimumDuration` go (and what does it mean)?

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

**Open question:** the non-HIP `Train` has `canDepartFromAnyTrack` (for
outstanding trains). HIP has no equivalent. Add it to `TrainRequest`?

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
**Decision: reference by name** (string keying into `Scenario.trainUnitTypes`).
Embedding is redundant and risks inconsistency.

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
- `priority`: dropped. The HIP version marks it deprecated; the solver
  always sets it to 1 and never reads it; the non-HIP comment about
  "lower means more important" appears to be a documentation error. If the
  generator never sets meaningful priorities and no one reads them, the field
  goes away.

**Open question:** confirm the generator can drop `priority` entirely. Are
there any code paths that emit non-1 values? (User says no — confirming for
the record.)

**C# note.** The C# `TaskSpec` retains `Priority` with a
`// TODO set deprecation? or remove wholesale?` comment, mirroring the same
unresolved question. The Pydantic model can be the place where it's
finalized; removing it from C# follows.

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
  direction the rest of the document argues for. **Decision pending** —
  switching to ID reference is cleaner but requires the evaluator to have
  access to the same `ShuntingUnit` registry the solver used.

**Open question:** is there a canonical proto file for `Plan` somewhere not
yet shared, or is the C# code the most authoritative version? If a proto
exists, worth comparing.

**Open question:** does the evaluator's expected input format match `Plan`
as it appears in the C# code, or does it expect something different? This
matters for sizing the C++ work.

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
   pick up changes.

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

## Next steps

1. ~~Reconcile this document against the C# records~~ — done; see "C#
   reconciliation notes" section above.
2. Resolve the open questions (collected at the end of this document for
   convenience).
3. Decide on `Plan` scope: same schema or separate, and what to do about
   `Plan.trackParts` and `Action.shuntingUnit` embedding.
4. Draft the Pydantic models in a `models/` package, one file per concept
   group (`location.py`, `scenario.py`, `train.py`, `plan.py`,
   `utilities.py`).
5. Generate JSON Schema from the Pydantic models and check the output
   against a sample of existing generator output (semantic diff, not byte
   diff).
6. Wire the generator's output path through Pydantic; verify byte-identical
   or semantically-identical JSON against the current protobuf-based output
   for a regression suite of scenarios.
7. Coordinate with the C# side on the small set of breaking changes
   (`displayName` no longer includes carriage count; `priority` dropped;
   `TrainUnit.type` dropped in favor of `typeDisplayName`; `ShuntingUnit.members`
   dropped in favor of `memberIDs`; `standingType` dropped). Update the C#
   readers to handle the new shape *before* switching the generator's
   output.
8. Cut over the generator; remove protobuf dependency.
9. Move on to the C++ evaluator using the now-stable JSON Schema as the
   contract.

## Collected open questions

For convenience, the open questions scattered through the document above:

- Are the three `Location` movement coefficients per-location or actually
  global constants?
- Are `Walking`, `Break`, `NonService` task types ever present in JSON the
  solver reads? If so, verify the C# deserializer handles them gracefully
  once the enum is extended to include these plus `StandIn`/`StandOut`.
- Confirm the `displayName` cleanup ("SLT" + carriages=4 instead of "SLT4").
- Does `trainUnitTypes` belong on `Scenario` (referenced by name) or
  embedded into each `TrainUnit`?
- Where does `Train.minimumDuration` (non-HIP) belong in the unified model,
  and what does it mean?
- Should `standingIndex` apply to `IncomingTrain` as well as
  `TrainRequest`?
- Should `canDepartFromAnyTrack` (non-HIP only) be added to `TrainRequest`?
- Confirm `TaskSpec.priority` can be dropped.
- `Resource`: approach deferred to evaluator migration. Three candidates:
  nullable fields with validator (current), explicit discriminator field,
  or inheritance with subclasses. See `Resource` section for details.
- Is there a canonical proto for `Plan` somewhere?
- Does the evaluator's expected `Plan` input format match what the C# code
  produces?
- The cross-cutting questions: naming conventions, schema distribution,
  hashability per model. (Schema versioning, forward-compatibility policy,
  and ID types are resolved — see cross-cutting section above.)

# Schema changelog

Tracks changes to the shared interchange `schemaVersion`, carried on
`Location`, `Scenario`, and `Plan` (see `unified-schema-design.md`). This is
independent of the tool release versions (`generator`, `hip`, `tors`) — it
increments only on breaking changes to the wire format, and all three repos
bump their local `EXPECTED_SCHEMA_VERSION` together when it does.

Mismatch behaviour is warn-and-continue: a missing or unexpected
`schemaVersion` produces a logged warning, not a hard reject.

## Unversioned — 2026-08-19

`Scenario.standingIndex` (in/outStanding trains) changed from
`Optional[float]` to `Optional[NonNegativeInt]`, and a new check rejects
ambiguous standing order: two or more standing units sharing a track must have
fully-specified, distinct `standingIndex` values (inStanding: required once
any one is set; outStanding: all-unset is fine, a mix of set/unset is not).
**Also deliberately not a version bump**, same reasoning shape as 2026-08-12:

- Nothing breaks. No fixture across `scenario-planning-inputs` has ever set a
  non-null `standingIndex` — checked directly, every occurrence in every
  committed `scenario_*.json`/`plan_*.json` is `null` — so the type narrowing
  changes nothing observable, and no track in the corpus has two or more
  standing units on it, so the new consistency check never fires today.
- The narrowing makes the schema honest about behaviour that already held one
  layer down: cTORS's `TrainGoal` already typed the field `const int`
  internally, silently truncating the wire double at construction. The
  evaluator needed no code change as a result; the solver did — its default
  for an absent index moved from `?? 0.0` to `?? 0` alongside the schema
  change, since it now reads an int rather than a double off the wire.

## Unversioned — 2026-08-12

`Location.trackParts`, `Plan.actions` and `Scenario.trainUnitTypes` became
required. **Deliberately not a version bump**, despite tightening the wire
format, and the reasoning is recorded here so it does not read as an oversight:

- Nothing breaks. All three fields were already emitted by every producer, in
  every one of the 143 fixtures in `scenario-planning-inputs` — and non-empty in
  every one, so even `minItems: 1` would have passed. The change makes existing
  practice enforceable rather than changing what anyone writes.
- A bump would have no mechanical effect anyway. Mismatch is warn-and-continue,
  so a consumer pinned to 1 reading a 2 logs a line and proceeds. The three
  repos would have paid the coordination cost of bumping
  `EXPECTED_SCHEMA_VERSION` together and bought nothing.

What this closes: `{}` validated as both a `Location` and a `Plan`, so a fixture
sweep reporting "N/N valid" was a weaker statement than it looked. It does
not close renamed or misspelled fields — `extra="forbid"` on `RailModel` already
rejects those — and it cannot make a *consumer* that reads a field with a silent
`.get(name, [])` default fail. What it does is let consumers drop that default
and index directly, which is where the actual protection lives.

`minItems` was considered and left off. It measures free today — no fixture has
an empty `trackParts`, `actions` or `trainUnitTypes` — but an empty plan is a
defensible representation of "nothing to do", and requiredness was the part
worth having.

## 1 — 2026-07-30

Initial version. `schemaVersion: 1` added to the top level of `Location`,
`Scenario`, and `Plan`.

# Schema changelog

Tracks changes to the shared interchange `schemaVersion`, carried on
`Location`, `Scenario`, and `Plan` (see `unified-schema-design.md`). This is
independent of the tool release versions (`generator`, `hip`, `tors`) — it
increments only on breaking changes to the wire format, and all three repos
bump their local `EXPECTED_SCHEMA_VERSION` together when it does.

Mismatch behaviour is warn-and-continue: a missing or unexpected
`schemaVersion` produces a logged warning, not a hard reject.

## 1 — 2026-07-30

Initial version. `schemaVersion: 1` added to the top level of `Location`,
`Scenario`, and `Plan`.

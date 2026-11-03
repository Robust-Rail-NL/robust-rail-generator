# Contributing

## Git hooks

Formatting and linting run through [`pre-commit`](https://pre-commit.com/);
see the README for the one-time `uv run pre-commit install`. The same
configuration ([`.pre-commit-config.yaml`](.pre-commit-config.yaml)) also
refuses a direct commit to `edge` (see the branch flow below). A plain
`git merge --no-ff` into `edge` that merges cleanly doesn't run the
`pre-commit` hook at all, so it is unaffected. If a merge conflicts, the
commit that concludes it does run the hook and is refused; finish it with
`SKIP=no-commit-to-branch git commit`. Like any hook, `--no-verify` skips
it — it is a backstop, not a guarantee.

## Image channels: `stable` and `edge`

The generator image is published under two channels:

- **`stable`** — built from `main` via [`docker-push.sh`](docker-push.sh),
  tagged `generator:$VERSION` (and `generator:latest` for a non-prerelease
  version). Every change lands here through its own feature branch and a
  reviewed PR into `main` — `stable` means "last reviewed, released
  version."
- **`edge`** — a fast, lower-ceremony channel for running a not-yet-reviewed
  fix without waiting for its PR into `main`. Built and pushed via
  [`docker-push-edge.sh`](docker-push-edge.sh) under the floating
  `generator:edge` tag, always overwritten by the newest push to the `edge`
  branch.

### Branch flow

- **Every change still goes through its own feature branch and PR into
  `main`.** `edge` does not replace that — it runs alongside it. Never
  commit directly to `edge`.
- **To get a fix onto `edge` early**, merge its feature branch into `edge`
  (`git merge --no-ff <branch>`) in addition to opening the normal PR into
  `main`. Once that PR is reviewed and merged, `edge` already has the
  content — nothing needs to be cherry-picked or re-applied.
- **`edge` only ever advances via merge commits** (`git merge --no-ff`),
  whether merging in a feature branch or catching up with `main`. Never
  rebase `edge`, and never fast-forward it — the point is for its history to
  show what was merged in and when, as a readable sequence of merge commits,
  not a flattened line that hides which branch each change came from.
- **Flow between `edge` and `main` is one-directional**: `main → edge`
  only, via periodic `git merge --no-ff main`. Nothing flows from `edge`
  back into `main` directly, since nothing should ever exist on `edge` that
  doesn't also exist on some reviewed feature branch (see above).
- One accepted gap: if `edge` is ever force-pushed or rebased despite the
  above, a dropped commit won't show up in `git log` — only `git reflog` or
  GitHub's Actions run history would have it. Treated as a reasonable
  tradeoff for a fast-moving channel; revisit only if that actually causes a
  real problem.

### Publishing `edge`

Currently manual only — run [`docker-push-edge.sh`](docker-push-edge.sh)
yourself from the `edge` branch (it checks and refuses to run from anywhere
else, or with uncommitted changes). There is no CI automation building or
pushing `edge` on every push to the branch. This is a deliberate choice, not
an oversight: wiring that up means a new category of CI workflow (deploy,
not just build/test) and storing GHCR push credentials as Actions secrets —
a real increase in attack surface for a channel that exists to move fast,
not to be hardened.

### Versioning `edge`

`edge` images don't reuse `pyproject.toml`'s `version` as-is (that's what
distinguishes a `stable` build). Instead:
`<release>-edge+<date>.<short-sha>`, e.g. `2.2.0-edge+20261103.a1b2c3d`.

- `edge` is its own semver prerelease identifier, not chained onto whatever
  prerelease suffix (if any) `pyproject.toml` currently holds — the release
  portion is always the bare `X.Y.Z`.
- The date and short SHA are semver build metadata (after the `+`), not part
  of the prerelease identifier — build metadata doesn't affect version
  precedence/sorting, which is correct here: an edge build should never be
  compared as if it were an ordered release, but a human or a bug report
  should still be able to trace a running image back to an exact commit and
  day.
- The string only goes into the image's
  `org.opencontainers.image.version` label; `pyproject.toml` is never
  modified. No git tag is created per edge build — the branch history itself
  is the record of what produced what.

### Tests on `edge`

[`.github/workflows/python.yml`](.github/workflows/python.yml) also runs on
every push to `edge`, so an unreviewed change gets the same test, lint and
example-freshness checks a PR into `main` would.

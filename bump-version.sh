#!/usr/bin/env bash
# Bump the generator version in pyproject.toml's [project] version field —
# the single source of truth used by docker-push.sh for the image tag and
# label. Re-locks uv.lock so its mirrored version field stays in sync.
#
# Also commits the change and creates a local, annotated git tag (vX.Y.Z),
# the same convention as `npm version`. Nothing is pushed — push the commit
# and tag yourself once you're happy with them, e.g.:
#   git push --follow-tags
set -euo pipefail

PYPROJECT="pyproject.toml"

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Working tree is not clean; commit or stash changes before bumping the version" >&2
    exit 1
fi

CURRENT=$(sed -n 's:^version = "\(.*\)"$:\1:p' "$PYPROJECT")
[[ -n "$CURRENT" ]] || { echo "Could not read version from $PYPROJECT" >&2; exit 1; }

usage() {
    echo "Usage: $0 <major|minor|patch|prerelease|X.Y.Z[-suffix]>" >&2
    echo "Current version: $CURRENT" >&2
    exit 1
}

[[ $# -eq 1 ]] || usage

RELEASE="${CURRENT%%-*}"
IFS='.' read -r MAJOR MINOR PATCH <<< "$RELEASE"
if [[ "$CURRENT" == *-* ]]; then
    PRE="${CURRENT#*-}"
else
    PRE=""
fi

case "$1" in
    major) NEW="$((MAJOR + 1)).0.0" ;;
    minor) NEW="$MAJOR.$((MINOR + 1)).0" ;;
    patch) NEW="$MAJOR.$MINOR.$((PATCH + 1))" ;;
    prerelease)
        if [[ "$PRE" =~ ^([A-Za-z]+)\.([0-9]+)$ ]]; then
            NEW="$RELEASE-${BASH_REMATCH[1]}.$((${BASH_REMATCH[2]} + 1))"
        else
            NEW="$RELEASE-alpha.1"
        fi
        ;;
    [0-9]*.[0-9]*.[0-9]*) NEW="$1" ;;
    *) usage ;;
esac

sed -i "s#^version = \"$CURRENT\"\$#version = \"$NEW\"#" "$PYPROJECT"
uv lock

git add "$PYPROJECT" uv.lock
git commit -m "Bump version to $NEW"
git tag -a "v$NEW" -m "v$NEW"

echo "Bumped version: $CURRENT -> $NEW"
echo "Created commit and tag v$NEW (not pushed — run 'git push --follow-tags' when ready)"

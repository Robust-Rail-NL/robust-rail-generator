#!/usr/bin/env bash
# Build and push the generator image to ghcr.io under the floating :edge tag —
# a fast, unvetted-fix channel alongside docker-push.sh's reviewed-release
# :$VERSION/:latest tags. See CONTRIBUTING.md for what edge is for and the
# branch flow it depends on.
#
# Must be run from the edge branch (checked below), since :edge is meant to
# always reflect whatever is currently on that branch — not whatever branch
# happened to be checked out locally. That branch must also be
# identical to origin/edge and the working tree clean (both checked below):
# publish only after pushing.
#
# The image version embedded in the build (the OCI label) is derived, not
# read from pyproject.toml as-is: <release>-edge+<date>.<short-sha>, e.g.
# 2.2.0-edge+20261103.a1b2c3d. The release portion is the [project] version
# currently committed in pyproject.toml, with any existing prerelease suffix
# stripped, since edge is its own prerelease identifier, not one chained onto
# another. The date+sha are semver build metadata (after the +), so they never
# affect version precedence/sorting — this is for a human or a bug report to
# trace a running image back to an exact commit and day, not for tooling to
# compare against. pyproject.toml itself is never touched.
#
# No git tag is created per edge build: branch history is the record (see
# CONTRIBUTING.md for the one gap that leaves — a force-push/rebase of edge).
#
# No :latest counterpart, unlike docker-push.sh's release images — :edge is
# the whole point of this channel; nothing else should ever point at an
# unreviewed build.
#
# Requires the same buildx builder as docker-push.sh — see its header comment
# for why (network=host, shared with sibling Robust-Rail-NL projects), and for
# why this also shares docker-push.sh's :buildcache ref.
set -euo pipefail
cd "$(dirname "$0")"

# BEGIN SHARED BLOCK: ghcr-login (identical in every repo's push scripts; edit all copies — checked by robust-rail-general/scripts/check_push_script_sync.py)
docker login ghcr.io
# Only the push needs auth; ghcr.io/robust-rail-nl is public for reads. Log
# out again once this script exits (success or failure) rather than leaving
# the credential sitting in the credential store, where every unrelated
# docker pull against ghcr.io (e.g. run_experiment.py's) ends up decrypting
# it for no reason.
trap 'docker logout ghcr.io' EXIT
# END SHARED BLOCK: ghcr-login

IMAGE="ghcr.io/robust-rail-nl/generator"
CACHE_REF="$IMAGE:buildcache"
BUILDER_NAME="robust-rail-builder"

# BEGIN SHARED BLOCK: edge-guards (identical in every repo's push scripts; edit all copies — checked by robust-rail-general/scripts/check_push_script_sync.py)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "edge" ]]; then
    echo "Refusing to publish :edge from branch '$BRANCH' — checkout edge first." >&2
    exit 1
fi

# The docker build context is the working tree, not the commit, so any
# uncommitted or untracked change would end up in an image whose version
# string claims a clean sha. Refuse rather than publish that.
if [[ -n "$(git status --porcelain)" ]]; then
    echo "Refusing to publish :edge from a dirty working tree — commit or stash first." >&2
    git status --short >&2
    exit 1
fi

# :edge must only ever reflect what is on origin/edge, so every published
# image traces back to a commit anyone can fetch. Refuse if local edge has
# unpushed commits (or is behind): push first, then publish.
git fetch --quiet origin edge
if [[ "$(git rev-parse HEAD)" != "$(git rev-parse origin/edge)" ]]; then
    echo "Refusing to publish :edge: local edge ($(git rev-parse --short HEAD)) differs from origin/edge ($(git rev-parse --short origin/edge)) — push (or pull) first." >&2
    exit 1
fi
# END SHARED BLOCK: edge-guards

RELEASE=$(sed -n 's:^version = "\(.*\)"$:\1:p' pyproject.toml)
[[ -n "$RELEASE" ]] || { echo "Could not read version from pyproject.toml" >&2; exit 1; }
RELEASE="${RELEASE%%-*}"

EDGE_VERSION="$RELEASE-edge+$(date -u +%Y%m%d).$(git rev-parse --short HEAD)"

# BEGIN SHARED BLOCK: buildx-builder (identical in every repo's push scripts; edit all copies — checked by robust-rail-general/scripts/check_push_script_sync.py)
if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --driver-opt network=host
fi
# END SHARED BLOCK: buildx-builder

docker buildx build \
    --builder "$BUILDER_NAME" \
    --platform linux/amd64,linux/arm64 \
    --build-arg "VERSION=$EDGE_VERSION" \
    -t "$IMAGE:edge" \
    --cache-to "type=registry,ref=$CACHE_REF,mode=max" \
    --cache-from "type=registry,ref=$CACHE_REF" \
    --push \
    .

echo "Pushed $IMAGE:edge (version $EDGE_VERSION)"

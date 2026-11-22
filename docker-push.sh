#!/usr/bin/env bash
# Build and push the multi-arch generator image to ghcr.io.
#
# The version is read from pyproject.toml's [project] version (the single
# source of truth — bump it there) and passed into the image as a
# build-arg, so the Dockerfile LABEL never needs a separate edit.
#
# Multi-arch matters even though this is "just Python": pydantic v2 bundles
# pydantic-core, a compiled Rust extension, so `pip install pydantic` pulls
# an architecture-specific wheel at build time. An image built on an amd64
# host contains amd64-only native code and either fails or runs under slow
# QEMU emulation on arm64 hosts (e.g. Apple Silicon, AWS Graviton).
#
# :latest is only applied to final, non-prerelease versions (no -rc./-beta./
# -alpha. suffix) — same reasoning as robust-rail-solver's docker-push.sh:
# :latest is what someone gets when they ask for the image without thinking
# about it, and that should never silently become a prerelease build partway
# through a release's rc/beta line.
#
# Requires a buildx builder using the "docker-container" driver with
# network=host. The default driver runs the BuildKit container in an
# isolated network namespace whose DNS resolution can fail to reach
# private/LAN DNS servers (seen as: "docker build" works, "docker buildx
# build" times out resolving a private host). network=host makes the
# builder share the host's network stack, avoiding that failure mode.
#
# BUILDER_NAME is shared with sibling Robust-Rail-NL projects (e.g.
# robust-rail-evaluator, robust-rail-solver) that need the same
# multi-arch/network=host setup — a buildx builder isn't tied to a specific
# repo or Dockerfile.
#
# --cache-to/--cache-from push and pull the build cache through a dedicated
# ":buildcache" tag on the same image (see robust-rail-planner's docker-push.sh
# for the mechanism and its cost — free here too, ghcr.io/robust-rail-nl is
# public). The builder stage's `uv sync` doesn't depend on VERSION at all, so
# unlike the other siblings this repo needed no Dockerfile reordering for the
# cache to actually pay off across releases — a version bump alone already
# reuses it.
#
# Refuses to run unless the working tree is clean and HEAD is the commit
# tagged v<version> (as created by bump-version.sh), with that tag pushed to
# origin. Pass -f to skip these checks.
set -euo pipefail
cd "$(dirname "$0")"

# BEGIN SHARED BLOCK: release-flags (identical in every repo's push scripts; edit all copies — checked by robust-rail-general/scripts/check_push_script_sync.py)
FORCE=0
while getopts f opt; do
    case $opt in
        f) FORCE=1 ;;
        *) echo "Usage: $0 [-f]" >&2; exit 2 ;;
    esac
done
# END SHARED BLOCK: release-flags

IMAGE="ghcr.io/robust-rail-nl/generator"
CACHE_REF="$IMAGE:buildcache"
BUILDER_NAME="robust-rail-builder"

VERSION=$(sed -n 's:^version = "\(.*\)"$:\1:p' pyproject.toml)
[[ -n "$VERSION" ]] || { echo "Could not read version from pyproject.toml" >&2; exit 1; }

# BEGIN SHARED BLOCK: release-guards (identical in every repo's push scripts; edit all copies — checked by robust-rail-general/scripts/check_push_script_sync.py)
# A release image is permanent, and :$VERSION / :latest is what consumers
# pull, so only publish a commit that bump-version.sh has tagged v$VERSION
# and whose tag is on origin (which also means the commit itself is pushed).
# The working tree must be clean too: the docker build uses the working
# tree, not the commit. -f skips all of these checks.
TAG="v$VERSION"
if [[ $FORCE -eq 1 ]]; then
    echo "WARNING: -f given, skipping the clean-tree / pushed-tag checks for $TAG." >&2
else
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "Refusing to publish $VERSION from a dirty working tree — commit or stash first (or use -f)." >&2
        git status --short >&2
        exit 1
    fi
    TAG_SHA=$(git rev-parse -q --verify "refs/tags/$TAG^{commit}") || {
        echo "Refusing to publish $VERSION: no local tag $TAG — run bump-version.sh, or use -f." >&2
        exit 1
    }
    if [[ "$TAG_SHA" != "$(git rev-parse HEAD)" ]]; then
        echo "Refusing to publish $VERSION: HEAD ($(git rev-parse --short HEAD)) is not the commit tagged $TAG ($(git rev-parse --short "$TAG_SHA")) — checkout $TAG, or use -f." >&2
        exit 1
    fi
    # Annotated tags list the tagged commit on the peeled ^{} line; a
    # lightweight tag has only the plain line.
    REMOTE_SHA=$(git ls-remote origin "refs/tags/$TAG^{}" | cut -f1 || true)
    [[ -n "$REMOTE_SHA" ]] || REMOTE_SHA=$(git ls-remote origin "refs/tags/$TAG" | cut -f1 || true)
    if [[ "$REMOTE_SHA" != "$TAG_SHA" ]]; then
        echo "Refusing to publish $VERSION: tag $TAG is not on origin at $(git rev-parse --short "$TAG_SHA") (or origin is unreachable) — git push origin $TAG, or use -f." >&2
        exit 1
    fi
fi
# END SHARED BLOCK: release-guards

# BEGIN SHARED BLOCK: ghcr-login (identical in every repo's push scripts; edit all copies — checked by robust-rail-general/scripts/check_push_script_sync.py)
docker login ghcr.io
# Only the push needs auth; ghcr.io/robust-rail-nl is public for reads. Log
# out again once this script exits (success or failure) rather than leaving
# the credential sitting in the credential store, where every unrelated
# docker pull against ghcr.io (e.g. run_experiment.py's) ends up decrypting
# it for no reason.
trap 'docker logout ghcr.io' EXIT
# END SHARED BLOCK: ghcr-login

TAGS=(-t "$IMAGE:$VERSION")
if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    TAGS+=(-t "$IMAGE:latest")
fi

# BEGIN SHARED BLOCK: buildx-builder (identical in every repo's push scripts; edit all copies — checked by robust-rail-general/scripts/check_push_script_sync.py)
if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --driver-opt network=host
fi
# END SHARED BLOCK: buildx-builder

docker buildx build \
    --builder "$BUILDER_NAME" \
    --platform linux/amd64,linux/arm64 \
    --build-arg "VERSION=$VERSION" \
    "${TAGS[@]}" \
    --cache-to "type=registry,ref=$CACHE_REF,mode=max" \
    --cache-from "type=registry,ref=$CACHE_REF" \
    --push \
    .

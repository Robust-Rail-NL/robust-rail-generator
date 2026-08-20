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
set -euo pipefail

IMAGE="ghcr.io/robust-rail-nl/generator"
BUILDER_NAME="robust-rail-builder"

VERSION=$(sed -n 's:^version = "\(.*\)"$:\1:p' pyproject.toml)
[[ -n "$VERSION" ]] || { echo "Could not read version from pyproject.toml" >&2; exit 1; }

TAGS=(-t "$IMAGE:$VERSION")
if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    TAGS+=(-t "$IMAGE:latest")
fi

if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --driver-opt network=host
fi

docker buildx build \
    --builder "$BUILDER_NAME" \
    --platform linux/amd64,linux/arm64 \
    --build-arg "VERSION=$VERSION" \
    "${TAGS[@]}" \
    --push \
    .

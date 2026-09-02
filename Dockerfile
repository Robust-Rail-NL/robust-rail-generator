FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

FROM python:3.12-slim

ARG VERSION=0.0.0
LABEL org.opencontainers.image.source="https://github.com/Robust-Rail-NL/robust-rail-generator" \
      org.opencontainers.image.description="Robust Rail Generator" \
      org.opencontainers.image.version="${VERSION}"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY pyproject.toml ./

COPY src/ src/

COPY data/ data/

ENV PATH="/app/.venv/bin:${PATH}"
ENTRYPOINT ["python", "src/main.py"]

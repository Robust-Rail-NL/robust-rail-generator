FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/Robust-Rail-NL/robust-rail-generator" \
      org.opencontainers.image.description="Robust Rail Generator" \
      org.opencontainers.image.version="2.0.0-alpha.1"

RUN pip install --no-cache-dir 'pydantic'

WORKDIR /app

COPY src/ src/

COPY data/ data/

ENTRYPOINT ["python", "src/main.py"]

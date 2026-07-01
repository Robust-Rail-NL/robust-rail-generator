FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/Robust-Rail-NL/robust-rail-generator" \
      org.opencontainers.image.description="Robust Rail Generator" \
      org.opencontainers.image.version="1.2.0"

RUN pip install --no-cache-dir 'protobuf>=3.19,<3.20'

WORKDIR /app

COPY src/ src/

COPY data/ data/

ENTRYPOINT ["python", "src/main.py"]

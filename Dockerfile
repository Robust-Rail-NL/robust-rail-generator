FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/Robust-Rail-NL/robust-rail-generator" \
      org.opencontainers.image.description="Robust Rail Generator" \
      org.opencontainers.image.version="0.2"

RUN pip install --no-cache-dir 'pydantic'

WORKDIR /app

COPY src/ src/

COPY data/ data/

ENTRYPOINT ["python", "src/main.py"]

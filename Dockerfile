FROM python:3.12-slim

RUN pip install --no-cache-dir protobuf

WORKDIR /app

COPY src/ src/

ENTRYPOINT ["python", "src/main.py"]

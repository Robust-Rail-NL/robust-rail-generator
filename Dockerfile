FROM python:3.12-slim

RUN pip install --no-cache-dir 'protobuf>=3.19,<3.20'

WORKDIR /app

COPY src/ src/

COPY data/ data/

ENTRYPOINT ["python", "src/main.py"]

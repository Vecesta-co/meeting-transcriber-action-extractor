FROM python:3.11-slim

WORKDIR /app

# Install system audio dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY fixtures ./fixtures

RUN pip install --no-cache-dir .

ENTRYPOINT ["meeting-transcriber"]
CMD ["info"]


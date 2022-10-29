# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster
WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python", "app.py"]

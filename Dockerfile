FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install gcc -y && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app/

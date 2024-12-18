FROM python:3.9.13-slim-buster

USER root

ARG PIP_VERSION=22.0.4

# Create non root user convergence_user
RUN adduser --quiet --disabled-password \
    --home /home/convergence_user \
    --shell /bin/bash convergence_user

# Set working directory.
WORKDIR /srv

# Set PYTHONPATH
ENV PYTHONPATH="/srv"

# Copy dependencies.
COPY ./requirements.dev.txt .

# Install dependencies.
RUN pip install --no-cache-dir --upgrade pip=="${PIP_VERSION}" \
 && pip install --no-cache-dir -r requirements.dev.txt

RUN apt-get update && apt-get install make

COPY . /srv

USER convergence_user
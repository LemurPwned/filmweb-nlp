FROM python:3.6-slim

WORKDIR /app 
COPY sentiment.py /app
COPY ss3_models/ /app

# config
RUN mkdir -p /var/www \
    && apt-get update \
    && apt-get install -y \
    build-essential \
    bash \
    python-dev \
    git \
    python3-pip \
    && pip3 install -U pip

RUN pip3 install -U \
    numpy \
    requests \
    && pip3 install pyss3

ENTRYPOINT [ "/bin/bash" ]
FROM python:3.6-slim

WORKDIR /app 
COPY NER.py /app

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

ENV SPACY_VERSION    2.0.18

# spacy
RUN pip3 install -U \
        numpy \
        requests \
    && pip3 install -U spacy==${SPACY_VERSION} \
    && python3 -m spacy download en   

ENTRYPOINT [ "/bin/bash" ]
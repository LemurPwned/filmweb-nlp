# FROM alpine:3.7

# WORKDIR /app

# RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
# RUN apk add --update --no-cache py3-numpy py3-pandas@testing 

# RUN apk --no-cache add musl-dev linux-headers g++ libstdc++

# RUN apk add --no-cache python3 python3-dev build-base libev-dev && \
#     pip3 install --upgrade pip && \
#     rm -r /root/.cache
    
# RUN ln -s /usr/include/locale.h /usr/include/xlocale.h 

# COPY requirements.txt /app
# RUN pip3 install -r requirements.txt




FROM python:3.6-slim

WORKDIR /app 

# config
RUN mkdir -p /var/www \
    && apt-get update \
    && apt-get install -y \
        build-essential \
        bash \
        libev-dev \
        python-dev \
        git \
        python3-pip \
    && pip3 install -U pip

ENV SPACY_VERSION    2.0.18

COPY . /app

COPY requirements.txt /app

# spacy
RUN pip3 install -U -r requirements.txt \
    && python3 -m spacy download en  \
    && pip3 install https://storage.googleapis.com/spacy-pl-public-models/pl_model-1.0.0.tar.gz 

ENTRYPOINT ["python3"]
CMD ["server.py"]
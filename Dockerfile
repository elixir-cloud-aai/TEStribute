##### BASE IMAGE #####
FROM python:3.9-slim-buster

##### METADATA #####
LABEL base.image="3.9-slim-buster"
LABEL version="1.1"
LABEL software="TEStribute"
LABEL software.version="0.2.1"
LABEL software.description="Flask microservice implementing the TEStribute task distribution logic as an API service."
LABEL software.website="https://github.com/elixir-europe/TEStribute"
LABEL software.documentation="https://github.com/elixir-europe/TEStribute"
LABEL software.license="https://github.com/elixir-europe/TEStribute/blob/master/LICENSE"
LABEL software.tags="General"
LABEL maintainer="alexander.kanitz@alumni.ethz.ch"
LABEL maintainer.organisation="Biozentrum, University of Basel"
LABEL maintainer.location="Klingelbergstrasse 50/70, CH-4056 Basel, Switzerland"
LABEL maintainer.lab="ELIXIR Cloud & AAI"
LABEL maintainer.license="https://spdx.org/licenses/Apache-2.0"

# Python UserID workaround for OpenShift/K8S
ENV LOGNAME=ipython
ENV USER=ipython

# Install general dependencies
RUN apt-get update && apt-get install -y nodejs openssl git build-essential python3-dev

## Set working directory
WORKDIR /app

## Copy Python requirements
COPY ./requirements.txt /app/requirements.txt

## Install Python dependencies
RUN cd /app \
  && pip install -r requirements.txt \
  && cd /

## Copy remaining app files
COPY ./ /app

## Install app
RUN cd /app \
  && python setup.py develop \
  && cd /


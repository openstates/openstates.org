FROM        python:3.5-jessie
MAINTAINER  James Turk <james@openstates.org>

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    binutils \
    libproj-dev \
    gdal-bin

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'en_US.UTF-8'
ENV LANGUAGE=en_US:en
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV WORKON_HOME=/opt/virt
RUN mkdir -p $WORKON_HOME


RUN mkdir -p /opt/openstates.org/
ADD . /opt/openstates.org
WORKDIR /opt/openstates.org
RUN pip install -r requirements.txt

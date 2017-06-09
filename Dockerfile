FROM        ubuntu:latest
MAINTAINER  James Turk <james@openstates.org>

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3.5 \
    git \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    python-virtualenv

RUN mkdir -p /opt/openstates.org/

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'en_US.UTF-8'
ENV LANGUAGE=en_US:en
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV WORKON_HOME=/opt/virt

RUN pip3 install pipenv

ADD . /opt/openstates.org
WORKDIR /opt/openstates.org

RUN pipenv --three install 

ENTRYPOINT [bash]

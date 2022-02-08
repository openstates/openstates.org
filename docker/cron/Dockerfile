FROM python:3.9
LABEL maintainer="James Turk <dev@jamesturk.net>"

# global environment settings
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING='utf-8' LANG='C.UTF-8'
STOPSIGNAL SIGINT

RUN BUILD_DEPS=" \
      python3-dev \
      git \
      build-essential \
      libpq-dev \
      libgeos-dev \
      libgdal-dev \
      libcap-dev \
      wget \
      postgresql-client \
      awscli \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS
RUN pip install poetry

ADD . /code
WORKDIR /code
RUN poetry install

FROM        python:3.6-alpine
MAINTAINER  James Turk <james@openstates.org>

ADD . /opt/openstates.org
WORKDIR /opt/openstates.org

RUN apk add --no-cache --virtual .build-dependencies \
    build-base && \
  apk add --no-cache \
    git \
    libffi-dev \
    libressl-dev \
    postgresql-dev && \
  apk add --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    gdal-dev \
    geos-dev && \
  pip install pipenv && \
  pipenv install --dev --system --deploy && \
  apk del .build-dependencies

ENV GDAL_LIBRARY_PATH /usr/lib/libgdal.so

CMD ["python", "manage.py", "runserver"]

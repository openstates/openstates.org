FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1
# based on https://www.caktusgroup.com/blog/2017/03/14/production-ready-dockerfile-your-python-django-app/

RUN mkdir /code/
WORKDIR /code/

EXPOSE 8000

RUN BUILD_DEPS=" \
      python3-dev \
      git \
      libpq-dev \
      libgeos-dev \
      libgdal-dev \
      wget \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS

ADD . /code/

ENV PYTHONDONTWRITEBYTECODE=1

RUN wget https://deb.nodesource.com/setup_10.x -O nodesource.sh \
    && bash nodesource.sh \
    && apt install -y nodejs \
    && npm ci \
    && npm run build

RUN set -ex \
    && python3.7 -m venv /venv \
    && /venv/bin/pip install -U pip poetry \
    && /venv/bin/poetry install

EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["/venv/bin/poetry", "run", "./manage.py"]
CMD ["runserver", "0.0.0.0:8000"]

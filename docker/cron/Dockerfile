FROM python:3.13-bookworm
LABEL maintainer="James Turk <dev@jamesturk.net>"

# global environment settings
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING='utf-8' LANG='C.UTF-8'
STOPSIGNAL SIGINT

COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
  UV_PYTHON_DOWNLOADS=never \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  PATH=/opt/venv/bin:$PATH

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

ADD . /code
WORKDIR /code
RUN uv sync --locked --no-dev --no-cache

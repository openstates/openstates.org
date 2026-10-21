FROM python:3.13-bookworm
LABEL maintainer="James Turk <dev@jamesturk.net>"

ARG UID=999

# global environment settings
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONIOENCODING='utf-8' \
  LANG='C.UTF-8'
STOPSIGNAL SIGINT

COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/
# venv lives outside /code so the dev bind mount (.:/code) doesn't hide it
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
  UV_PYTHON_DOWNLOADS=never \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  PATH=/opt/venv/bin:$PATH

RUN apt-get --allow-releaseinfo-change update -qq \
    && apt-get install -y --no-install-recommends -qq \
        postgresql-client \
        libpq5 \
        libgdal32 \
        libpcre3 \
        python3-dev \
        git \
        build-essential \
        libpq-dev \
        libgeos-dev \
        libgdal-dev \
        libcap-dev \
        libpcre3-dev \
        awscli

# copy code and entrypoint in
ADD . /code/
WORKDIR /code/
COPY docker/uwsgi/custom-entrypoint /usr/local/bin
COPY docker/uwsgi/node.pin /etc/apt/preferences.d/node

RUN curl https://deb.nodesource.com/setup_16.x -SsLo nodesource.sh \
    && bash nodesource.sh \
    && apt-get install -y -qq --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN npm ci \
    && npm run build

# everything after here as openstates user
RUN useradd -u $UID -Ulmr -d /home/openstates openstates \
    && install -d -o openstates -g openstates /opt/venv /code/collected_static
USER openstates:openstates

RUN uv sync --locked --no-dev --group deploy --no-cache

USER root
RUN apt-get remove -y -qq build-essential \
      gcc \
      g++ \
      make \
      python3-dev \
      git \
      libpq-dev \
      libgeos-dev \
      libgdal-dev \
      libcap-dev \
      libpcre3-dev \
    && apt-get autoremove -y
USER openstates:openstates

# uwsgi config
ENV UWSGI_MASTER=1 \
  UWSGI_HTTP_AUTO_CHUNKED=1 \
  UWSGI_HTTP_KEEPALIVE=1 \
  UWSGI_LAZY_APPS=1 \
  UWSGI_WSGI_ENV_BEHAVIOR=holy \
  UWSGI_MODULE=web.wsgi:application \
  UWSGI_BUFFER_SIZE=8096 \
  UWSGI_HARAKIRI=30 \
  UWSGI_SINGLE_INTERPRETER=1 \
  UWSGI_SOCKET=:9999 \
  UWSGI_VIRTUALENV=/opt/venv

ENTRYPOINT ["custom-entrypoint"]
CMD ["uwsgi", "--show-config"]

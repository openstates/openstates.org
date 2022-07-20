FROM python:3.9
LABEL maintainer="James Turk <dev@jamesturk.net>"

# global environment settings
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONIOENCODING='utf-8' \
  LANG='C.UTF-8'
STOPSIGNAL SIGINT

RUN apt-get --allow-releaseinfo-change update -qq \
    && apt-get install -y --no-install-recommends -qq \
        postgresql-client \
        uwsgi \
        libpq5 \
        libgdal28 \
        python3-dev \
        git \
        build-essential \
        libpq-dev \
        libgeos-dev \
        libgdal-dev \
        libcap-dev \
        uwsgi-src \
        awscli \
    && cd /usr/lib/uwsgi/plugins \
    && uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python39"

# copy code and entrypoint in
ADD . /code/
WORKDIR /code/
COPY docker/uwsgi/custom-entrypoint /usr/local/bin

RUN curl https://deb.nodesource.com/setup_lts.x -SsLo nodesource.sh \
    && bash nodesource.sh \
    && apt-get install -y -qq --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && npm ci \
    && npm run build
RUN pip --no-cache-dir --disable-pip-version-check install poetry

# everything after here as openstates user
RUN useradd -Ulmr -d /home/openstates -G sudo openstates
USER openstates:openstates

RUN poetry install --no-dev \
    && rm -r ~/.cache/pypoetry/cache ~/.cache/pypoetry/artifacts/

RUN sudo apt-get remove -y -qq build-essential \
      python3-dev \
      git \
      libpq-dev \
      libgeos-dev \
      libgdal-dev \
      libcap-dev \
      uwsgi-src \
    && sudo apt-get autoremove -y

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
  UWSGI_PLUGIN=python39 \
  UWSGI_SOCKET=:9999

ENTRYPOINT ["custom-entrypoint"]
CMD ["uwsgi", "--show-config"]

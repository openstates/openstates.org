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
      uwsgi \
      uwsgi-src \
      awscli \
    " \
    && apt-get --allow-releaseinfo-change update && apt-get install -y --no-install-recommends $BUILD_DEPS

RUN cd /usr/lib/uwsgi/plugins && uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python39"

# copy code and entrypoint in
ADD . /code/
WORKDIR /code/
COPY docker/uwsgi/custom-entrypoint /usr/local/bin
RUN chmod a+x /usr/local/bin/custom-entrypoint

RUN wget https://deb.nodesource.com/setup_lts.x -O nodesource.sh \
    && bash nodesource.sh \
    && apt install -y nodejs \
    && npm ci \
    && npm run build
RUN pip install poetry


# everything after here as openstates user
RUN groupadd -r openstates && useradd --no-log-init -r -g openstates openstates
RUN mkdir /home/openstates && chown openstates:openstates /home/openstates
USER openstates:openstates

RUN poetry install

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

FROM tiangolo/uvicorn-gunicorn:python3.8

# install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# install npm
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

ENV APP_MODULE=web.asgi:application

COPY pyproject.toml poetry.lock package.json package-lock.json /app/
RUN poetry install --no-root --no-dev
RUN npm install
COPY . /app
RUN npm run build

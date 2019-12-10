# openstates.org

[![CircleCI](https://circleci.com/gh/openstates/openstates.org.svg?style=svg)](https://circleci.com/gh/openstates/openstates.org)

This project powers the 2019 OpenStates.org, including the API.

## Developing

### Dependencies
* [Python 3.7](https://www.python.org/) (with [poetry](https://poetry.eustace.io/))
* PostgreSQL 11
* PostGIS 2.5
* recent version of npm

### Installing

Ensure you have Docker installed, everything else will be managed there.

#### Getting a database replica:

On first run, you'll need to populate your database with real data.

1) Start the database instance via `docker-compose up -d db`
2) Run `docker-compose run --rm --entrypoint ./docker/download-db.sh django`, this takes a while but downloads a copy of the database and restores it.

#### Running locally

`docker-compose up` should start django & the database, then browse to http://localhost:8000

#!/bin/sh

set -e

poetry run ./manage.py migrate
DATABASE_URL=postgis://openstates:openstates@db:5432/openstatesorg poetry run os-initdb
poetry run ./manage.py update_materialized_views --initial

PYTHONPATH=docker/ poetry run ./manage.py shell -c "import testdata"

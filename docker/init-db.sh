#!/bin/sh

set -ex
unset DATABASE_URL

docker-compose run --rm -e PYTHONPATH=docker/ --entrypoint 'poetry run ./manage.py migrate' django
# add test data
docker-compose run --rm -e PYTHONPATH=docker/ --entrypoint 'poetry run ./manage.py shell -c "import testdata"' django

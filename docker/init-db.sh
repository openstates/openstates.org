#!/bin/sh

set -ex
unset DATABASE_URL

docker compose run --rm -e PYTHONPATH=docker/ --entrypoint './manage.py migrate' django
# add test data
docker compose run --rm -e PYTHONPATH=docker/ --entrypoint './manage.py shell -c "import testdata"' django

#!/bin/sh

# don't want to accidentally test on prod db, always use local db
unset DATABASE_URL

docker-compose run --rm --entrypoint "uv run pytest --reuse-db $*" django

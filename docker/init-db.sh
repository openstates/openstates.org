#!/bin/sh

set -e

WHICH="2020-01"
FILE=schema.pgdump
if [ ! -f "$FILE" ]; then
  wget https://data.openstates.org/postgres/schema/$WHICH-schema.pgdump -O $FILE
fi
PGPASSWORD=openstates pg_restore --host db --user openstates -d openstatesorg $FILE;
# rm $FILE;


FILE=data.pgdump
if [ ! -f "$FILE" ]; then
  wget https://data.openstates.org/postgres/monthly/$WHICH-public.pgdump -O $FILE
fi
PGPASSWORD=openstates pg_restore --disable-triggers --host db --user openstates -d openstatesorg $FILE;
# rm $FILE;

poetry run ./manage.py update_materialized_views --initial

PYTHONPATH=docker/ poetry run ./manage.py shell -c "import testdata"

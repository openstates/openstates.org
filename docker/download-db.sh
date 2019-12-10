#!/bin/sh

set -e

FILE=latest.pgdump
if [ ! -f "$FILE" ]; then
  wget https://openstates-backups.s3.amazonaws.com/public/daily/2019-12-07-public.pgdump -O $FILE
fi
PGPASSWORD=openstates pg_restore --host db --user openstates -d openstatesorg $FILE;
# rm $FILE;

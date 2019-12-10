#!/bin/sh

set -e

wget https://openstates-backups.s3.amazonaws.com/public/daily/2019-12-07-public.pgdump -O latest.pgdump
PGPASSWORD=openstates pg_restore --host db --user openstates -d openstatesorg latest.pgdump;
rm latest.pgdump;

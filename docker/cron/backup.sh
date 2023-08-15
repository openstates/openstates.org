#!/bin/sh
set -e

#####
# Quick note:
# pg_dump -Fc is single-threaded, but *is* compressed
# Improving storage and performance could be achieved with
# a combination of '-j' (parallel table export)
# and piping to gzip or zstd
# but that complicates the process for restoration
# so we should only do it once we need to
####

# backup everything to private archive
#echo "Extracting full backup..."
#pg_dump -Fc openstatesorg > openstatesorg.pgdump
#echo "Shipping full backup to s3"
#aws s3 cp openstatesorg.pgdump "s3://openstates-backups/full-backup/$(date +%Y-%m-%d)-openstatesorg.pgdump" > /dev/null
#rm -f openstatesorg.pgdump

# layered approach for public
echo "Executing public schema-only backup..."
pg_dump -Fc openstatesorg --schema-only > schema.pgdump
aws s3 cp --acl public-read schema.pgdump "s3://data.openstates.org/postgres/schema/$(date +%Y-%m)-schema.pgdump" > /dev/null
rm -f schema.pgdump

echo "Executing public data backup..."
pg_dump -Fc openstatesorg --data-only \
  --table=opencivicdata* \
  --table=django_migrations \
  --table=django_content_type \
  --table=django_site \
  > public.pgdump

echo "Uploading public backups to s3..."
aws s3 cp --acl public-read public.pgdump "s3://data.openstates.org/postgres/daily/$(date +%Y-%m-%d)-public.pgdump" > /dev/null
# only upload monthly dump on the first of the month
[ "$(date +%d)" -eq 1 ] && aws s3 cp --acl public-read public.pgdump "s3://data.openstates.org/postgres/monthly/$(date +%Y-%m)-public.pgdump" > /dev/null
rm -f public.pgdump

#echo "Extracting geo backup..."
#pg_dump -Fc geo > openstates-geo.pgdump
#echo "Shipping full backup to s3"
#aws s3 cp openstates-geo.pgdump "s3://openstates-backups/full-backup/$(date +%Y-%m-%d)-openstates-geo.pgdump" > /dev/null
#rm -f openstates-geo.pgdump

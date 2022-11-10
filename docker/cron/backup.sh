#!/bin/sh
set -e

# backup everything to private archive
echo "Extracting full backup..."
pg_dump -Fc openstatesorg | gzip > openstatesorg.pgdump.gz
echo "Shipping full backup to s3"
aws s3 cp openstatesorg.pgdump.gz "s3://openstates-backups/full-backup/$(date +%Y-%m-%d)-openstatesorg.pgdump.gz"


# layered approach for public
echo "Executing public schema-only backup..."
pg_dump -Fc openstatesorg --schema-only | gzip > schema.pgdump.gz
echo "Executing public data backup..."
pg_dump -Fc openstatesorg --data-only \
  --table=opencivicdata* \
  --table=django_migrations \
  --table=django_content_type \
  --table=django_site \
  | gzip > public.pgdump.gz

echo "Uploading public backups to s3..."
aws s3 cp --acl public-read schema.pgdump.gz "s3://data.openstates.org/postgres/schema/$(date +%Y-%m)-schema.pgdump.gz"
aws s3 cp --acl public-read public.pgdump.gz "s3://data.openstates.org/postgres/daily/$(date +%Y-%m-%d)-public.pgdump.gz"
aws s3 cp --acl public-read public.pgdump.gz "s3://data.openstates.org/postgres/monthly/$(date +%Y-%m)-public.pgdump.gz"

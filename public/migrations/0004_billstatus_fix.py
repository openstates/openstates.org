from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0003_billstatus"),
    ]

    operations = [
        migrations.RunSQL(
            """
           DROP MATERIALIZED VIEW public_billstatus;
           CREATE MATERIALIZED VIEW public_billstatus AS
           SELECT b.id as bill_id,
           (SELECT MIN(date) from opencivicdata_billaction WHERE bill_id = b.id) as "first_action_date",
           (SELECT MAX(date) from opencivicdata_billaction WHERE bill_id = b.id) as "latest_action_date",
           (SELECT MAX(date) from opencivicdata_billaction WHERE bill_id = b.id and classification @> ARRAY['passage']) as "latest_passage_date",
           (SELECT description from opencivicdata_billaction WHERE bill_id = b.id ORDER by date DESC LIMIT 1) as "latest_action_description"
           FROM opencivicdata_bill b;
           CREATE UNIQUE INDEX public_billstatus_pk ON public_billstatus(bill_id);
           """,
            """
           DROP MATERIALIZED VIEW public_billstatus
           """,
        ),
    ]

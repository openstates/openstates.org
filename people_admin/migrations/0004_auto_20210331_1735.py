# Generated by Django 3.1.7 on 2021-03-31 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("people_admin", "0003_deltaset_pr_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="unmatchedname",
            options={
                "permissions": [("can_match_names", "Can use the name matching tool.")]
            },
        ),
    ]

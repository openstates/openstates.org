# Generated by Django 3.2 on 2021-05-05 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people_admin", "0005_auto_20210401_1532"),
    ]

    operations = [
        migrations.AlterField(
            model_name="persondelta",
            name="data_changes",
            field=models.JSONField(),
        ),
    ]
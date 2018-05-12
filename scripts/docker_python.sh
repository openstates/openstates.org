#!/bin/sh

echo "Running migrations"
python manage.py migrate

echo "Populating Database from pupa"
python manage.py loaddivisions us

echo "Running Server"
python manage.py runserver 0.0.0.0:8000

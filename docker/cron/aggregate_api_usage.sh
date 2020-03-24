#!/bin/sh

poetry run ./manage.py aggregate_api_usage /var/log/uwsgi/app/openstates.log*

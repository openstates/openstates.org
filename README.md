# The new openstates.org, and API v2

## Summary

### Front-end

The front-end is a Django site, augmented by React for particular pages that require state management.

### API

_Needs to be filled out by @jamesturk_

### Database

The database in the OCD schema, managed by Django and powered by PostGIS.

## Dependencies

- Python 3.5
- PostgreSQL 9.4
- PostGIS 2.3

## Running locally

```
# Install dependencies, ideally within a virtual environment
pip install -r requirements.txt

# Set up the database
createdb openstates
psql postgres://localhost/openstates -c "CREATE EXTENSION postgis;"
export DATABASE_URL=postgis://localhost/openstates
./manage.py migrate
./manage.py loaddivisions us
# Now, run any `pupa update` scrapes you need to import data into the database
# Alternatively, load a database dump that already contains scraped data

# Run the server; now, open up the API or front-end locally!
./manage.py runserver
```

# openstates.org

[![Build Status](https://travis-ci.com/openstates/openstates.org.svg?branch=develop)](https://travis-ci.com/openstates/openstates.org)

This project powers the 2019 OpenStates.org, including the API.

## Developing

### Dependencies
* [Python 3.6](https://www.python.org/) (with [poetry](https://poetry.eustace.io/))
* PostgreSQL 10
* PostGIS 2.4
* recent version of npm

### Installing

#### Python & Django

Install dependencies
```
poetry install
```

Create the database and user
```
psql -c "CREATE USER openstates CREATEDB SUPERUSER;" -U postgres
createdb openstatesorg
```

Populate the database

If you have access to a `pgdump` file (for example, from the `openstates-backups` AWS S3 bucket with a filename ending in `openstatesorg.pgdump`), then you can load the data from that:
```
pg_restore --dbname openstatesorg PATH_TO_PGDUMP_FILE
```

Without a `pgdump` file to restore from, you can instantiate an Open Civic Data database yourself and afterwards use `pupa update` scrapes to populate it with data:

```
psql openstates -c "CREATE EXTENSION postgis;"
DATABASE_URL=postgis://localhost/openstates ./manage.py migrate
DATABASE_URL=postgis://localhost/openstates ./manage.py loaddivisions us
```

#### Frontend

Install frontend dependencies
```
npm install
```

Do an initial build of assets
```
npm run build
```


### Running the project locally

Start up the Django webserver.
```
./manage.py runserver
```

Start up webpack to watch and build any changes to static files.
```
npm run start
```

Now you can open up `localhost:8000` in your browser to see the project running locally.

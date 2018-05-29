# The new openstates.org, and API v2

## Summary

### FrontEnd 
The frontend is a Django site, augmented by React for particular pages that require state management.

### API

GraphQL-based API, using Graphene.

### Database

The database is in [Open Civic Data](https://github.com/opencivicdata) format, managed by Django and powered by PostGIS.

## Developing
### Dependencies
* [Python 3.5](https://www.python.org/) (with [pip](https://pip.pypa.io/en/stable/) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/))
* PostgreSQL 9.4
* PostGIS 2.3
* [nvm](https://github.com/creationix/nvm#install-script)


### Installing

#### Python & Django
Create a Python 3 virtual environment
```
mkvirtualenv --python=$(which python3) openstates
```

Install dependencies
```
pip install -r requirements.txt
```

Create the database

```
createdb openstates
```

Populate the database

If you have access to an Open Civic Data `pgdump` file (for example, from the `openstates-backups` AWS S3 bucket with a filename ending in `openstatesorg.pgdump`), then you can load the data from that:

```
pg_restore --dbname openstates PATH_TO_PGDUMP_FILE
```

Without a `pgdump` file to restore from, you can instantiate an Open Civic Data database yourself and afterwards use `pupa update` scrapes to populate it with data:

```
psql openstates -c "CREATE EXTENSION postgis;"
DATABASE_URL=postgis://localhost/openstates ./manage.py migrate
DATABASE_URL=postgis://localhost/openstates ./manage.py loaddivisions us
```

#### Frontend 

Use nvm to install the correct version of Node.js
```
nvm install
```

Install frontend dependencies
```
npm install
```

Do an initial build of assets
```
npm run build
```


### Running the project locally

Start up the Django webserver. Make sure that your environment's `DATABASE_URL` exists, and starts with `postgis://`, such as `postgis://localhost/openstates`.

```
./manage.py runserver
```

Start up webpack to watch and build any changes to static files.
```
npm run start
```

Now you can open up `localhost:8000` in your browser to see the project running locally.

# The new openstates.org, and API v2

## Summary

### FrontEnd 
The frontend is a Django site, augmented by React for particular pages that require state management.

### API

_Needs to be filled out by @jamesturk_

### Database

The database in the OCD schema, managed by Django and powered by PostGIS.

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

Set up the database
_Skip this step if you can load a database dump that already contains scraped data_
```
createdb openstates
psql postgres://localhost/openstates -c "CREATE EXTENSION postgis;"
export DATABASE_URL=postgis://localhost/openstates
./manage.py migrate
./manage.py loaddivisions us
```
Now, run any `pupa update` scrapes you need to import data into the database


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
Start up the Django webserver.
```
./manage.py runserver
```

Start up webpack to watch and build any changes to static files.
```
npm run start
```

Now you can open up `localhost:8000` in your browser to see the project running locally.

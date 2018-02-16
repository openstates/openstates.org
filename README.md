# The new openstates.org


## Front-end

The front-end is bootstrapped using `create-react-app` for React.js. To run locally, run `yarn` or `npm install`, and then `yarn run start` or `npm run start`. This will build all Sass files to CSS, then serve the React app located in `src`.

For issues with the build system, check [the user guide](https://github.com/facebookincubator/create-react-app/blob/master/packages/react-scripts/template/README.md).

## Back-end

The back-end consists of an OCD Python database. While this project is under heavy development it is recommended you install as follows:

```
$ mkvirtualenv newos

$ git clone git@github.com:opencivicdata/python-opencivicdata.git
$ cd python-opencivicdata
$ python setup.py develop
$ cd ..

$ git clone git@github.com:opencivicdata/pupa.git
$ cd pupa
$ python setup.py develop
$ cd ..

$ git clone git@github.com:openstates/new-openstates.org.git
$ cd new-openstates.org
$ pip install -r requirements.txt

$ ./manage.py migrate
$ ./manage.py runserver
```

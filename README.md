# new-openstates.org

While this project is under heavy development it is recommended you install as follows:

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


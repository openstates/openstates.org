# openstates.org

This repository contains the code responsible for openstates.org, the website and v2 API (graphql).

## Make changes

Changes should be made in a local checkout of the repo. There is a bit of setup to get a working DB and environment,
which by default will run in docker.

* Branch off of the `develop` branch
* Follow instructions for [working on openstates.org](https://docs.openstates.org/contributing/openstates-org/)
from the docs.
* Quirks I ran into:
  * `npm run start` did not actually make JS/CSS available when I hit the app at `localhost:8000`. Instead I ran `npm run build` and then rebuilt the docker containers with `docker compose build`, finally started them again.
  * For some reason my DB ended up missing a row representing the Django Site. This resulted in something like "Site not found" error when trying to log in/register. Solution was: 
    * Get shell on the running container `sudo docker exec -it openstatesorg-django-1 /bin/bash`
    * In that shell run `poetry run python manage.py shell --settings=web.settings`
    * In THAT shell run `from django.contrib.sites.models import Site;Site.objects.get_or_create(domain='openstates.org', name='openstates.org')`
    * However for me this created an entry with `SITE_ID` of `2` when `1` is the necessary value to match up with `web/settings.py`
* Merge your feature branch into `develop` (this launches a workflow that publishes docker images)
* Merge `develop` into `main` (this gets code into the branch that should be used for deploy)

## Deploy

* Check out the `main` branch of this repository to your local workstation
* You will need permissions on the Open States AWS account to be able to interact with 
at least the parameter store and the EC2 instance where the site is deployed
* You need the SSH private key to access the EC2 instance, stored at `~/.ssh/openstates-master.pem`
* Ensure that you have the correct python version installed via pyenv
* Install the [aws cli tool](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* Install [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible),
such that `ansible-playbook` command is available. (There are recent changes in the package re: `ansible-community`
which might necessitate a change in our deploy script. For now, I just deployed a somewhat older version via
my operating system's package manager)
* In your copy of this repo, with `main` checked out, run the command, which runs a script which runs a set
of ansible tasks:

```
poetry run inv deploy
```

All the steps should be OK. It's normal to see a lot of output of things changing. You should get to
something like the following near the end:

```
PLAY RECAP ************************************
openstates.org             : ok=41   changed=6 
```


## Links

* [Issues](https://github.com/openstates/issues/issues)
* [Discussions](https://github.com/openstates/issues/discussions)
* [Contributor's Guide](https://docs.openstates.org/contributing/)
* [Documentation](https://docs.openstates.org/contributing/openstates-org/)
* [Code of Conduct](https://docs.openstates.org/code-of-conduct/)

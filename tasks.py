from invoke import task
import datetime
import os
import shutil


def start_docker_db(c):
    # turn on docker database if not already on
    if shutil.which("docker-compose"):
        c.run("docker-compose --profile db up -d db")
    else:
        c.run("docker compose --profile db up -d db")
    os.environ[
        "DATABASE_URL"
    ] = "postgres://openstates:openstates@localhost:5405/openstatesorg"


def get_next_tag(c):
    prefix = datetime.datetime.today().strftime("%Y.%m")
    release_num = 1

    last_tag = c.run("git tag", hide="out").stdout.splitlines()[-1]

    print("last tag is", last_tag)
    while f"{prefix}.{release_num}" <= last_tag:
        release_num += 1

    return f"{prefix}.{release_num:02}"


def poetry_install(c):
    c.run("poetry install")


@task
def test(c, args="", docker_db=True):
    if docker_db:
        start_docker_db(c)
    c.run("poetry run pytest --ds web.test_settings --reuse-db " + args, pty=True)


@task
def lint(c):
    c.run(
        "poetry run flake8 --show-source --statistics --ignore=E203,E501,W503 --max-line-length=120",
        pty=True,
    )
    c.run("black --check --diff .", pty=True)


@task
def runserver(c, docker_db=True):
    if docker_db:
        start_docker_db(c)
    c.run("poetry run ./manage.py runserver", pty=True)


@task
def deploy(c):
    # for ansible on OSX
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    NEWRELIC_APP_ID = c.run(
        "aws ssm get-parameter --name /site/NEWRELIC_OPENSTATES_APP_ID --with-decryption | jq -r .Parameter.Value",
        hide="out",
    ).stdout.strip()
    NEWRELIC_API_KEY = c.run(
        "aws ssm get-parameter --name /site/NEWRELIC_API_KEY --with-decryption | jq -r .Parameter.Value",
        hide="out",
    ).stdout.strip()
    SENTRY_RELEASE_ENDPOINT = c.run(
        "aws ssm get-parameter --name /site/SENTRY_RELEASE_ENDPOINT --with-decryption | jq -r .Parameter.Value",
        hide="out",
    ).stdout.strip()

    with c.cd("ansible"):
        c.run("ansible-playbook openstates.yml -i inventory/", pty=True)

    # tag the release in git and on sentry and newrelic
    next_tag = get_next_tag(c)
    c.run(
        f'curl {SENTRY_RELEASE_ENDPOINT} -X POST -H "Content-Type: application/json" -d \'{{"version": "{next_tag}"}}\''
    )
    c.run(
        f"""curl -X POST \
    "https://api.newrelic.com/v2/applications/{NEWRELIC_APP_ID}/deployments.json" \
         -H "X-Api-Key:{NEWRELIC_API_KEY}" -i \
         -H "Content-Type: application/json" \
         -d \
    '{{ "deployment": {{ "revision": "{next_tag}", "changelog": "", "description": "", "user": "" }} }}'
  """
    )
    c.run(f"git tag {next_tag}")
    c.run("git push --tags")


# npm stuff: not sure these provide any value right now...


@task
def npm_build(c):
    """build node scripts"""
    c.run("npm run build", pty=True)


@task
def npm_watch(c):
    c.run("npm run start", pty=True)

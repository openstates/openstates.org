from invoke import task
import datetime
import os


def start_docker_db(c):
    # turn on docker database if not already on
    c.run("docker-compose up -d db")
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

    return f"{prefix}.{release_num}"


def poetry_install(c):
    c.run("poetry install")


@task
def test(c, args="", docker_db=True):
    if docker_db:
        start_docker_db(c)
    c.run("poetry run pytest --ds web.test_settings --reuse-db " + args, pty=True)


@task
def runserver(c, docker_db=True):
    if docker_db:
        start_docker_db(c)
    c.run("poetry run ./manage.py runserver", pty=True)


@task
def deploy(c):
    # for ansible on OSX
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    # NEWRELIC_APP_ID = c.run(
    #     "aws ssm get-parameter --name /site/NEWRELIC_OPENSTATES_APP_ID --with-decryption | jq -r .Parameter.Value",
    #     hide="out"
    # ).stdout.strip()
    # NEWRELIC_API_KEY = c.run(
    #     "aws ssm get-parameter --name /site/NEWRELIC_API_KEY --with-decryption | jq -r .Parameter.Value",
    #     hide="out"
    # ).stdout.strip()
    SENTRY_RELEASE_ENDPOINT = c.run(
        "aws ssm get-parameter --name /site/SENTRY_RELEASE_ENDPOINT --with-decryption | jq -r .Parameter.Value",
    ).stdout.strip()

    with c.cd("ansible"):
        c.run("ansible-playbook openstates.yml -i inventory/", pty=True)

    next_tag = get_next_tag(c)
    c.run(
        f'curl {SENTRY_RELEASE_ENDPOINT} -X POST -H "Content-Type: application/json" -d \'{{"version": "{next_tag}"}}\''
    )
    c.run(f"git tag {next_tag}")
    c.run("git push --tags")


# npm stuff: not sure these provide any value right now...


@task
def npm_build(c):
    """ build node scripts """
    c.run("npm run build", pty=True)


@task
def npm_watch(c):
    c.run("npm run start", pty=True)

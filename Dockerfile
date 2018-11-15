FROM python:3.6
MAINTAINER  James Turk <james@openstates.org>

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    git \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    python-virtualenv

WORKDIR /opt/openstates.org

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'en_US.UTF-8'
ENV LANGUAGE=en_US:en
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV WORKON_HOME=/opt/virt

COPY Pipfile* ./
RUN pip3 install pipenv
RUN pip install -U pipenv
RUN pipenv --three install --system

COPY . .

EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]

import datetime


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

from enum import Enum
from django.db import models
from openstates.data.models import LegislativeSession, Person


class NameStatus(Enum):
    # not matched yet
    UNMATCHED = "U"

    # matched to a legislator (matched_person will be true)
    MATCHED_PERSON = "P"

    # for cases where this isn't a valid sponsor
    SOURCE_ERROR = "E"

    # unresolvable
    IGNORED = "I"


NAME_STATUS_CHOICES = (
    (NameStatus.UNMATCHED, "Unmatched"),
    (NameStatus.MATCHED_PERSON, "Matched Person"),
    (NameStatus.SOURCE_ERROR, "Source Error"),
    (NameStatus.IGNORED, "Ignored"),
)


class UnmatchedName(models.Model):
    session = models.ForeignKey(LegislativeSession, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    sponsorships = models.PositiveIntegerField()
    votes = models.PositiveIntegerField()

    status = models.CharField(
        max_length=1, choices=NAME_STATUS_CHOICES, default=NameStatus.UNMATCHED
    )
    matched_person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)

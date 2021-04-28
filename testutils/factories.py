import random
from openstates.data.models import Organization, Bill, LegislativeSession, Person, Post


def create_test_bill(
    session,
    chamber,
    *,
    sponsors=0,
    actions=0,
    votes=0,
    versions=0,
    documents=0,
    sources=0,
    subjects=None,
    identifier=None,
):
    chamber = Organization.objects.get(classification=chamber)
    session = LegislativeSession.objects.get(identifier=session)
    b = Bill.objects.create(
        identifier=identifier or ("Bill " + str(random.randint(1000, 9000))),
        title="Random Bill",
        legislative_session=session,
        from_organization=chamber,
        subject=subjects or [],
    )
    for n in range(sponsors):
        b.sponsorships.create(name="Someone")
    for n in range(actions):
        b.actions.create(
            description="Something", order=n, organization=chamber, date="2020-06-01"
        )
    for n in range(votes):
        b.votes.create(
            identifier="A Vote Occurred",
            organization=chamber,
            legislative_session=session,
        )
    for n in range(versions):
        b.versions.create(note="Version")
    for n in range(documents):
        b.documents.create(note="Document")
    for n in range(sources):
        b.sources.create(url="http://example.com")
    return b


def create_test_vote(bill, *, yes_count=0, no_count=0, yes_votes=None, no_votes=None):
    vote = bill.votes.create(
        identifier="test vote",
        organization=bill.from_organization,
        legislative_session=bill.legislative_session,
    )
    vote.counts.create(option="yes", value=yes_count)
    vote.counts.create(option="no", value=no_count)
    for name in yes_votes or []:
        vote.votes.create(option="yes", voter_name=name)
    for name in no_votes or []:
        vote.votes.create(option="no", voter_name=name)


def create_test_person(name, *, org, district, party):
    p = Person.objects.create(
        name=name,
        primary_party=party,
        current_jurisdiction=org.jurisdiction,
        current_role={
            "org_classification": org.classification,
            "district": district,
            "division_id": "ocd-division/123",
            "title": "Title",
        },
    )
    post = Post.objects.create(organization=org, label=district)
    p.memberships.create(post=post, organization=org)
    party, _ = Organization.objects.get_or_create(name=party, classification="party")
    p.memberships.create(organization=party)
    return p

from django.db import IntegrityError
from django.contrib.postgres.search import SearchVector
from openstates.data.models import (
    Division,
    Jurisdiction,
    Organization,
    Person,
    Bill,
    VoteEvent,
    SearchableBill,
)
from openstates.importers.computed_fields import update_bill_fields

from .static import JURISDICTIONS


def populate_db():
    for abbr, jur in JURISDICTIONS.items():
        d = Division.objects.get_or_create(
            id=f"ocd-division/country:us/state:{abbr}",
            name=jur["name"],
        )
        if isinstance(d, tuple):
            d = d[0]
        j = Jurisdiction.objects.get_or_create(
            id=f"ocd-jurisdiction/country:us/state:{abbr}/government",
            name=jur["name"],
            division=d,
        )
        if isinstance(j, tuple):
            j = j[0]
        for session in jur["sessions"]:
            try:
                j.legislative_sessions.create(
                    identifier=session, name=session, start_date=f"{session}-01-01"
                )
            except IntegrityError:
                # duplicate key, so just skip
                pass
        leg = Organization.objects.get_or_create(
            jurisdiction=j,
            classification="legislature",
            name=f"{jur['name']} Legislature",
        )
        if isinstance(leg, tuple):
            leg = leg[0]
        for chamber in jur["chambers"]:
            try:
                Organization.objects.create(
                    jurisdiction=j,
                    parent=leg,
                    classification=chamber,
                    name=f"{jur['name']} {'House' if chamber == 'lower' else 'Senate'}",
                )
            except IntegrityError:
                # duplicate key, so just skip
                pass
        for person in jur.get("people", []):
            _make_person(jur, person)

        for bill in jur.get("bills", []):
            _make_bill(jur, bill)

        # populate bill computed data
        for bill in Bill.objects.all().filter(
            legislative_session__jurisdiction__name__in=[jur["name"]],
        ):
            update_bill_fields(bill)


def _make_person(state, person):
    org = Organization.objects.get(
        jurisdiction__name=state, classification=person["chamber"]
    )
    party, _ = Organization.objects.get_or_create(
        classification="party", name=person["party"]
    )
    jurisdiction = Jurisdiction.objects.get(name=state)
    abbr = jurisdiction.abbreviation
    chamber_letter = person["chamber"][0]
    district = person["district"]
    div, _ = Division.objects.get_or_create(
        id=f"ocd-division/country:us/state:{abbr}/sld{chamber_letter}:{district.lower()}",
        name=f"Division {district}",
    )
    try:
        post = org.posts.create(
            label=district,
            division=div,
            role="Representative" if person["chamber"] == "lower" else "Senator",
        )
    except IntegrityError:
        # duplicate key, so just skip
        pass
    try:
        district = int(district)
    except ValueError:
        pass
    p = Person.objects.get_or_create(
        name=person["name"],
        primary_party=party.name,
        current_jurisdiction=jurisdiction,
        current_role={
            "org_classification": person["chamber"],
            "district": person["district"],
            "division_id": div.id,
            "title": post.role,
        },
    )
    if isinstance(p, tuple):
        p = p[0]
    try:
        p.memberships.create(post=post, organization=org)
    except IntegrityError:
        # duplicate key, so just skip
        pass
    try:
        p.memberships.create(organization=party)
    except IntegrityError:
        # duplicate key, so just skip
        pass
    if "end_date" in person:
        for m in p.memberships.all():
            m.end_date = person["end_date"]
            m.save()
        p.current_role = None
        p.save()
    for position in person.get("old_positions", []):
        old_org = Organization.objects.get(
            jurisdiction__name=state, classification=position["chamber"]
        )
        post = old_org.posts.get_or_create(
            label=position["district"],
            role="Representative" if position["chamber"] == "lower" else "Senator",
        )
        if isinstance(post, tuple):
            post = post[0]
        p.memberships.create(post=post, org=org, end_date=position["end_date"])
    return p


def _make_bill(name, bill):
    state = Jurisdiction.objects.get(name=name)
    org = state.organizations.get(classification=bill["chamber"])
    b = Bill.objects.get_or_create(
        id=f"ocd-bill/{bill['uid']}",
        title=bill.get("title", "An example bill"),
        identifier=bill["identifier"],
        legislative_session=bill["session"],
        from_organization=org,
        classification=bill.get("classifications", ["bill"]),
        subject=[bill.get("subjects", ["examples"])],
    )
    for abst in bill.get("abstracts", []):
        try:
            b.abstracts.create(abstract=abst)
        except IntegrityError:
            pass
    for title in bill.get("other_titles", []):
        try:
            b.other_titles.create(title=title)
        except IntegrityError:
            pass
    for identifer in bill.get("other_identifiers", []):
        try:
            b.other_identifiers.create(identifier="HCA 1")
        except IntegrityError:
            pass
    try:
        action = b.actions.create(
            description="Introduced",
            order=10,
            organization=org,
            date=f"{bill['session']}-01-01",
        )
        action.related_entities.create(
            name=org.name,
            entity_type="organization",
            organization=org,
        )
    except IntegrityError:
        # duplicate key, so just skip
        pass

    # add vote events to every bill
    for n in range(2):
        try:
            ve = VoteEvent.objects.create(
                bill=b,
                legislative_session=bill["session"],
                motion_text="Motion Text",
                organization=org,
                result="passed",
            )
        except IntegrityError:
            # duplicate key, so just skip all steps for this one
            continue
        try:
            ve.counts.create(option="yes", value=6)
        except IntegrityError:
            # duplicate key, so just skip
            pass
        try:
            ve.counts.create(option="no", value=3)
        except IntegrityError:
            # duplicate key, so just skip
            pass
        for m in range(5):
            try:
                ve.votes.create(option="yes", voter_name="Voter")
            except IntegrityError:
                # duplicate key, so just skip
                pass

    for doc in bill.get("documents", []):
        try:
            d = b.documents.create(note=doc["note"])
            d.links.create(url=doc["link"])
        except IntegrityError:
            pass
    for source in bill.get("sources", []):
        try:
            b.sources.create(url=source)
        except IntegrityError:
            pass
    for version in bill.get("versions", []):
        d = b.versions.create(note=version["note"], date=f"{bill['session']}-01-01")
        for link in version.get("links", []):
            link = d.links.create(url=version["link"], media_type="text/plain")
            if link.get("searchable", None):
                SearchableBill.objects.create(
                    bill=b,
                    version_link=link,
                    all_titles=b.title,
                    raw_text=link["searchable"]["text"],
                    is_error=False,
                    search_vector="",
                )
                SearchableBill.objects.update(
                    search_vector=(
                        SearchVector("all_titles", weight="A", config="english")
                        + SearchVector("raw_text", weight="B", config="english")
                    )
                )
    return b

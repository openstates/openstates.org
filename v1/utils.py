from collections import defaultdict
from . import static
from utils.common import jid_to_abbr


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def expand_date(date):
    if not date:
        return ""
    return date + " 00:00:00" if len(date) == 10 else date


def convert_post(post):
    abbr = jid_to_abbr(post.organization.jurisdiction_id)
    return {
        "division_id": post.division_id,
        "boundary_id": post.division_id,
        "name": post.label,
        "chamber": post.organization.classification,
        "abbr": abbr,
        "legislators": [],  # TODO?
        "num_seats": 1,
        "id": f"{abbr}-{post.organization.classification}-{post.label}",
    }


def v1_metadata(abbr, jurisdiction):
    orgs = {o.classification: o for o in jurisdiction.chambers}

    chambers = {}
    for chamber in ("upper", "lower"):
        if chamber in orgs:
            try:
                role = orgs[chamber].posts.all()[0].role
            except IndexError:
                role = ""
            chambers[chamber] = {"name": orgs[chamber].name, "title": role}

    sessions = {}
    for session in jurisdiction.legislative_sessions.all():
        sessions[session.identifier] = {
            "display_name": session.name,
            "type": session.classification,
        }
        for d in ("start_date", "end_date"):
            if getattr(session, d):
                sessions[session.identifier][d] = expand_date(getattr(session, d))

    try:
        latest_update = jurisdiction.latest_run.strftime(DATE_FORMAT)
    except AttributeError:
        latest_update = "2000-01-01 00:00:00"

    return {
        "id": abbr,
        "name": jurisdiction.name,
        "abbreviation": abbr,
        "legislature_name": orgs["legislature"].name,
        "legislature_url": jurisdiction.url,
        "chambers": chambers,
        "session_details": sessions,
        "latest_update": latest_update,
        "capitol_timezone": static.TIMEZONES[abbr],
        "terms": static.TERMS[abbr],
        "feature_flags": [],
        "latest_csv_date": "2018-11-03 00:00:00",
        "latest_csv_url": f"https://data.openstates.org/legacy/csv/{abbr}.zip",
        "latest_json_date": "2018-11-03 00:00:00",
        "latest_json_url": f"https://data.openstates.org/legacy/json/{abbr}.zip",
    }


def convert_action(a):
    return {
        "date": expand_date(a.date),
        "action": a.description,
        "type": [static.ACTION_MAPPING.get(c, "other") for c in a.classification],
        "related_entities": [],
        "actor": a.organization.classification,
    }


def convert_sponsor(sp):
    return {
        "leg_id": None,  # TODO - needed?
        "type": sp.classification,
        "name": sp.entity_name,
    }


def convert_vote(v, bill_chamber, state, bill_id):
    counts = {c.option: c.value for c in v.counts.all()}
    votes = {"yes": [], "no": [], "other": []}
    for pv in v.votes.all():
        if pv.option == "yes":
            votes["yes"].append({"leg_id": None, "name": pv.voter_name})
        elif pv.option == "no":
            votes["no"].append({"leg_id": None, "name": pv.voter_name})
        else:
            votes["other"].append({"leg_id": None, "name": pv.voter_name})

    return {
        "session": v.legislative_session.identifier,
        "id": "~not available~",
        "vote_id": "~not available~",
        "motion": v.motion_text,
        "date": v.start_date,
        "passed": v.result == "pass",
        "bill_chamber": bill_chamber,
        "state": state,
        "bill_id": bill_id,
        "chamber": v.organization.classification,
        "yes_count": counts.get("yes", 0),
        "no_count": counts.get("no", 0),
        "other_count": counts.get("other", 0),
        "yes_votes": votes["yes"],
        "no_votes": votes["no"],
        "other_votes": votes["other"],
        "sources": [{"url": s.url} for s in v.sources.all()],
        "type": "other",  # always the same
    }


def convert_versions(version_list):
    versions = []

    for v in version_list:
        for link in v.links.all():
            versions.append(
                {
                    "mimetype": link.media_type,
                    "url": link.url,
                    "doc_id": "~not available~",
                    "name": v.note,
                }
            )
    return versions


def convert_bill(b, include_votes):
    try:
        abstract = b.abstracts.all()[0].abstract
    except IndexError:
        abstract = ""

    chamber = b.from_organization.classification
    state = jid_to_abbr(b.legislative_session.jurisdiction_id)

    try:
        openstates_id = b.legacy_mapping.all()[0].legacy_id
    except IndexError:
        openstates_id = ""

    if include_votes:
        votes = [convert_vote(v, chamber, state, openstates_id) for v in b.votes.all()]
    else:
        votes = None

    return {
        "title": b.title,
        "summary": abstract,
        "created_at": b.created_at.strftime(DATE_FORMAT),
        "updated_at": b.updated_at.strftime(DATE_FORMAT),
        "id": openstates_id,
        "all_ids": [openstates_id],
        "chamber": chamber,
        "state": state,
        "session": b.legislative_session.identifier,
        "type": b.classification,
        "bill_id": b.identifier,
        "actions": [convert_action(a) for a in b.actions.all()],
        "sources": [{"url": s.url} for s in b.sources.all()],
        "sponsors": [convert_sponsor(sp) for sp in b.sponsorships.all()],
        "versions": convert_versions(b.versions.all()),
        "documents": convert_versions(b.documents.all()),
        "alternate_titles": [alt.title for alt in b.other_titles.all()],
        "votes": votes,
        "action_dates": {
            "first": expand_date(b.first_action_date),
            "last": expand_date(b.latest_action_date),
            # TODO - needed?
            "passed_upper": None,
            "passed_lower": None,
            "signed": None,
        },
        "scraped_subjects": b.subject,
        "alternate_bill_ids": [],
        "subjects": [],
        "companions": [],
    }


def convert_legislator(leg):
    if leg.given_name and leg.family_name:
        first_name = leg.given_name
        last_name = leg.family_name
        suffixes = ""
    else:
        last_name = leg.name
        suffixes = first_name = ""

    legacy_ids = [
        oid.identifier
        for oid in leg.identifiers.all()
        if oid.scheme == "legacy_openstates"
    ]

    if not legacy_ids:
        legacy_ids = ["~not available~"]

    party = leg.primary_party
    state = jid_to_abbr(leg.current_jurisdiction_id)
    chamber = None
    district = None

    if leg.current_role:
        chamber = leg.current_role["org_classification"]
        district = leg.current_role["district"]

    email = None
    offices = defaultdict(dict)
    for cd in leg.contact_details.all():
        offices[cd.note][cd.type] = cd.value
        if cd.type == "email" and not email:
            email = cd.value

    active = bool(chamber and district)

    try:
        url = leg.links.all()[0].url
    except IndexError:
        url = ""

    return {
        "id": legacy_ids[0],
        "leg_id": legacy_ids[0],
        "all_ids": legacy_ids,
        "full_name": leg.name,
        "first_name": first_name,
        "last_name": last_name,
        "suffix": suffixes,
        "photo_url": leg.image,
        "url": url,
        "email": email,
        "party": party,
        "chamber": chamber,
        "district": district,
        "state": state,
        "sources": [{"url": s.url} for s in leg.sources.all()],
        "active": active,
        "roles": [
            {
                "term": static.TERMS[state][-1]["name"],
                "district": district,
                "chamber": chamber,
                "state": state,
                "party": party,
                "type": "member",
                "start_date": None,
                "end_date": None,
            }
        ]
        if active
        else [],
        "offices": [
            {
                "name": label,
                "fax": details.get("fax"),
                "phone": details.get("voice"),
                "email": details.get("email"),
                "address": details.get("address"),
                "type": "capitol" if "capitol" in label.lower() else "district",
            }
            for label, details in offices.items()
        ],
        "old_roles": {},
        "middle_name": "",
        "country": "us",
        "level": "state",
        "created_at": leg.created_at.strftime(DATE_FORMAT),
        "updated_at": leg.updated_at.strftime(DATE_FORMAT),
    }

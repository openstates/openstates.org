import uuid
import random
from opencivicdata.core.models import Division, Jurisdiction, Organization, Person
from opencivicdata.legislative.models import Bill


def make_random_bill():
    state = random.choice(Jurisdiction.objects.all())
    session = random.choice(state.legislative_sessions.all())
    org = state.organizations.get(classification=random.choice(('upper', 'lower')))
    b = Bill.objects.create(id='ocd-bill/' + str(uuid.uuid4()),
                            title='Bill Title',
                            identifier=(random.choice(('HB', 'SB', 'HR', 'SR')) +
                                        str(random.randint(1000, 3000))),
                            legislative_session=session,
                            from_organization=org,
                            classification=[random.choice(['bill', 'resolution'])],
                            subject=[random.choice('abcdefghijklmnopqrstuvwxyz')
                                     for _ in range(10)],
                            )
    b.actions.create(description='Introduced', order=10, organization=org)
    return b


def make_person(name, state, chamber, district, party):
    org = Organization.objects.get(jurisdiction__name=state, classification=chamber)
    party, _ = Organization.objects.get_or_create(classification='party', name=party)
    post = org.posts.create(label=district)
    p = Person.objects.create(name=name)
    p.memberships.create(post=post, organization=org)
    p.memberships.create(organization=party)
    return p


def populate_db():
    for abbr, state in (('ak', 'Alaska'), ('wy', 'Wyoming')):
        d = Division.objects.create(id='ocd-division/country:us/state:' + abbr,
                                    name=state)
        j = Jurisdiction.objects.create(id='ocd-jurisdiction/country:us/state:' + abbr,
                                        name=state, division=d)
        j.legislative_sessions.create(identifier='2017', name='2017')
        j.legislative_sessions.create(identifier='2018', name='2018')

        leg = Organization.objects.create(jurisdiction=j, classification='legislature',
                                          name=state + ' Legislature')
        Organization.objects.create(jurisdiction=j, parent=leg,
                                    classification='lower', name=state + ' House')
        Organization.objects.create(jurisdiction=j, parent=leg,
                                    classification='upper', name=state + ' Senate')

    alaska = Jurisdiction.objects.get(name='Alaska')
    house = alaska.organizations.get(classification='lower')

    # AK House
    amanda = make_person('Amanda Adams', 'Alaska', 'lower', '1', 'Republican')
    make_person('Bob Birch', 'Alaska', 'lower', '2', 'Republican')
    make_person('Carrie Carr', 'Alaska', 'lower', '3', 'Democratic')
    make_person('Don Dingle', 'Alaska', 'lower', '4', 'Republican')
    # AK Senate
    ellen = make_person('Ellen Evil', 'Alaska', 'upper', 'A', 'Independent')
    make_person('Frank Fur', 'Alaska', 'upper', 'B', 'Democratic')
    # Ellen used to be a house member
    post = house.posts.create(label='5')
    ellen.memberships.create(post=post, organization=house, end_date='2017-01-01')

    # WY House (multi-member districts)
    make_person('Greta Gonzalez', 'Wyoming', 'lower', '1', 'Democratic')
    make_person('Hank Horn', 'Wyoming', 'lower', '1', 'Republican')

    b1 = Bill.objects.create(id='ocd-bill/1', title='Moose Freedom Act', identifier='HB 1',
                             legislative_session=alaska.legislative_sessions.get(
                                 identifier='2018'),
                             from_organization=house,
                             classification=['bill', 'constitutional amendment'],
                             subject=['nature'],
                             )
    b1.abstracts.create(abstract='Grants all moose equal rights under the law.')
    b1.abstracts.create(abstract='Ensure moose freedom.')
    b1.other_titles.create(title='Moosemendment')
    b1.other_titles.create(title='Moose & Reindeer Freedom Act')
    b1.other_titles.create(title='M.O.O.S.E.')
    b1.other_identifiers.create(identifier='HCA 1')
    b1.other_identifiers.create(identifier='SB 1')
    a = b1.actions.create(description='Introduced', order=10, organization=house)
    a.related_entities.create(name='Amanda Adams', entity_type='person', person=amanda)
    b1.actions.create(description='Amended', order=20, organization=house)
    a = b1.actions.create(description='Passed House', order=30, organization=house)
    a.related_entities.create(name='House', entity_type='organization', organization=house)

    b1.sponsorships.create(primary=True, classification='sponsor', name='Adam One')
    b1.sponsorships.create(primary=False, classification='cosponsor', name='Beth Two')
    d = b1.documents.create(note='Fiscal Note')
    d.links.create(url='https://example.com/fn')
    d = b1.documents.create(note='Legal Justification')
    d.links.create(url='https://example.com/lj')
    d = b1.versions.create(note='First Draft')
    d.links.create(url='https://example.com/1.txt', media_type='text/plain')
    d.links.create(url='https://example.com/1.pdf', media_type='application/pdf')
    d = b1.versions.create(note='Final Draft')
    d.links.create(url='https://example.com/f.txt', media_type='text/plain')
    d.links.create(url='https://example.com/f.pdf', media_type='application/pdf')
    b1.sources.create(url='https://example.com/s1')
    b1.sources.create(url='https://example.com/s2')
    b1.sources.create(url='https://example.com/s3')

    rb = Bill.objects.create(id='ocd-bill/3', title='Alces alces Freedom Act',
                             identifier='SB 9',
                             legislative_session=alaska.legislative_sessions.get(
                                 identifier='2018'),
                             from_organization=alaska.organizations.get(classification='upper'),
                             classification=['bill', 'constitutional amendment'],
                             subject=['nature'],
                             )
    b1.related_bills.create(related_bill=rb, identifier='SB 9', legislative_session='2018',
                            relation_type='companion'
                            )

    for x in range(24):
        make_random_bill()

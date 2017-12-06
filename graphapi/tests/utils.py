import uuid
import random
from opencivicdata.core.models import Division, Jurisdiction, Organization
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
                            subject=[random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(10)],
                            )
    return b


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
    session = alaska.legislative_sessions.get(identifier='2018')
    house = alaska.organizations.get(classification='lower')

    b1 = Bill.objects.create(id='ocd-bill/1', title='Moose Freedom Act', identifier='HB 1',
                             legislative_session=session, from_organization=house,
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
    b1.actions.create(description='Introduced', order=10, organization=house)
    b1.actions.create(description='Amended', order=20, organization=house)
    b1.actions.create(description='Passed House', order=30, organization=house)
    # TODO: add related_entities & related bill
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

    for x in range(25):
        make_random_bill()

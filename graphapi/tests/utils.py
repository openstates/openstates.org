from opencivicdata.core.models import Division, Jurisdiction, Organization
from opencivicdata.legislative.models import Bill


def populate_db():
    d = Division.objects.create(id='ocd-division/country:us/state:ak', name='Alaska')
    j = Jurisdiction.objects.create(id='ocd-jurisdiction/country:us/state:ak', name='Alaska',
                                    division=d)
    session = j.legislative_sessions.create(identifier='2018', name='2018')
    legislature = Organization.objects.create(jurisdiction=j, classification='legislature',
                                              name='Alaska Legislature')
    house = Organization.objects.create(jurisdiction=j, parent=legislature,
                                        classification='lower', name='Alaska House')
    b1 = Bill.objects.create(id='ocd-bill/123', title='Moose Freedom Act', identifier='HB 1',
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

    b2 = Bill.objects.create(id='ocd-bill/abc', title='North Pole Protection Act',
                             identifier='HB 2', legislative_session=session,
                             from_organization=house, classification=['bill'],
                             subject=['nature', 'holidays'])

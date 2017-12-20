import graphene
from django.db.models import Prefetch
from opencivicdata.legislative.models import Bill, BillActionRelatedEntity, PersonVote
from .common import OCDBaseNode, DjangoConnectionField
from .core import (LegislativeSessionNode, OrganizationNode, IdentifierNode,
                   PersonNode, LinkNode)
from .optimization import optimize


def jurisdiction_query(jurisdiction):
    query = {}
    if jurisdiction.startswith('ocd-jurisdiction'):
        query['legislative_session__jurisdiction_id'] = jurisdiction
    else:
        query['legislative_session__jurisdiction__name'] = jurisdiction
    return query


class BillAbstractNode(graphene.ObjectType):
    abstract = graphene.String()
    note = graphene.String()
    date = graphene.String()


class BillTitleNode(graphene.ObjectType):
    title = graphene.String()
    note = graphene.String()


class BillIdentifierNode(IdentifierNode):
    note = graphene.String()


class RelatedEntityNode(graphene.ObjectType):
    name = graphene.String()
    entity_type = graphene.String()
    organization = graphene.Field(OrganizationNode)
    person = graphene.Field(PersonNode)


class BillSponsorshipNode(RelatedEntityNode):
    primary = graphene.Boolean()
    classification = graphene.String()


class RelatedBillNode(graphene.ObjectType):
    identifier = graphene.String()
    legislative_session = graphene.String()
    relation_type = graphene.String()

    related_bill = graphene.Field('graphapi.legislative.BillNode')


class BillActionNode(graphene.ObjectType):
    organization = graphene.Field(OrganizationNode)
    description = graphene.String()
    date = graphene.String()
    classification = graphene.List(graphene.String)
    order = graphene.Int()
    extras = graphene.String()
    vote = graphene.Field('graphapi.legislative.VoteEventNode')

    related_entities = graphene.List(RelatedEntityNode)

    def resolve_related_entities(self, info):
        if 'related_entities' not in getattr(self, '_prefetched_objects_cache', []):
            return optimize(self.related_entities.all(), info, None, ['organization', 'person'])
        else:
            return self.related_entities.all()


class MimetypeLinkNode(graphene.ObjectType):
    media_type = graphene.String()
    url = graphene.String()
    text = graphene.String()


class BillDocumentNode(graphene.ObjectType):
    note = graphene.String()
    date = graphene.String()
    links = graphene.List(MimetypeLinkNode)

    def resolve_links(self, info):
        return self.links.all()


class BillNode(OCDBaseNode):
    legislative_session = graphene.Field(LegislativeSessionNode)
    identifier = graphene.String()
    title = graphene.String()
    from_organization = graphene.Field(OrganizationNode)
    classification = graphene.List(graphene.String)
    subject = graphene.List(graphene.String)

    # related fields
    abstracts = graphene.List(BillAbstractNode)
    other_titles = graphene.List(BillTitleNode)
    other_identifiers = graphene.List(BillIdentifierNode)
    actions = graphene.List(BillActionNode)
    sponsorships = graphene.List(BillSponsorshipNode)
    related_bills = graphene.List(RelatedBillNode)
    documents = graphene.List(BillDocumentNode)
    versions = graphene.List(BillDocumentNode)
    sources = graphene.List(LinkNode)
    votes = DjangoConnectionField('graphapi.legislative.VoteConnection')

    def resolve_abstracts(self, info):
        return self.abstracts.all()

    def resolve_other_titles(self, info):
        return self.other_titles.all()

    def resolve_other_identifiers(self, info):
        return self.other_identifiers.all()

    def resolve_actions(self, info):
        if 'actions' not in getattr(self, '_prefetched_objects_cache', []):
            return optimize(
                self.actions.all(), info,
                [('.relatedEntities',
                  Prefetch('related_entities',
                           BillActionRelatedEntity.objects.all().select_related(
                               'organization', 'person')
                           )
                  )],
                ['.organization'])
        else:
            return self.actions.all()

    def resolve_sponsorships(self, info):
        return self.sponsorships.all()

    def resolve_documents(self, info):
        if 'documents' not in getattr(self, '_prefetched_objects_cache', []):
            return optimize(self.documents.all(), info, ['.links'])
        else:
            return self.documents.all()

    def resolve_versions(self, info):
        if 'versions' not in getattr(self, '_prefetched_objects_cache', []):
            return optimize(self.versions.all(), info, ['.links'])
        else:
            return self.documents.all()

    def resolve_sources(self, info):
        return self.sources.all()

    def resolve_votes(self, info):
        if 'votes' not in getattr(self, '_prefetched_objects_cache', []):
            return optimize(self.votes.all(), info, [
                '.counts',
                ('.votes', Prefetch('votes', PersonVote.objects.all().select_related('voter'))),
             ])
        else:
            return self.votes.all()

    def resolve_related_bills(self, info):
        if 'related_bills' not in getattr(self, '_prefetched_objects_cache', []):
            return optimize(self.related_bills.all(), info, None, ['.relatedBill'])
        else:
            return self.related_bills.all()


class BillConnection(graphene.relay.Connection):
    class Meta:
        node = BillNode

    max_items = 100


class VoteCountNode(graphene.ObjectType):
    option = graphene.String()
    value = graphene.Int()


class PersonVoteNode(graphene.ObjectType):
    option = graphene.String()
    voter_name = graphene.String()
    voter = graphene.Field(PersonNode)
    note = graphene.String()


class VoteEventNode(OCDBaseNode):
    identifier = graphene.String()
    motion_text = graphene.String()
    motion_classification = graphene.List(graphene.String)
    start_date = graphene.String()
    end_date = graphene.String()
    result = graphene.String()

    organization = graphene.Field(OrganizationNode)
    bill_action = graphene.Field(BillActionNode)
    # not used for now since only path into VoteEvent is via Bill
    # legislative_session = graphene.Field(LegislativeSessionNode)
    # bill = graphene.Field(BillNode)

    # related entities
    votes = graphene.List(PersonVoteNode)
    counts = graphene.List(VoteCountNode)
    sources = graphene.List(LinkNode)

    def resolve_votes(self, info):
        return self.votes.all()

    def resolve_counts(self, info):
        return self.counts.all()

    def resolve_sources(self, info):
        return self.sources.all()


class VoteConnection(graphene.relay.Connection):
    class Meta:
        node = VoteEventNode


class LegislativeQuery:
    bill = graphene.Field(BillNode,
                          id=graphene.String(),
                          jurisdiction=graphene.String(),
                          session=graphene.String(),
                          identifier=graphene.String(),
                          )
    bills = DjangoConnectionField(BillConnection,
                                  jurisdiction=graphene.String(),
                                  session=graphene.String(),
                                  chamber=graphene.String(),
                                  updated_since=graphene.String(),
                                  subject=graphene.String(),
                                  classification=graphene.String(),
                                  )

    def resolve_bills(self, info,
                      before=None, after=None, first=None, last=None,
                      jurisdiction=None, chamber=None, session=None,
                      updated_since=None, classification=None,
                      subject=None,
                      ):
        # bill_id/bill_id__in
        # q (full text)
        # sponsor_id
        bills = Bill.objects.all()

        if jurisdiction:
            bills = bills.filter(**jurisdiction_query(jurisdiction))
        if chamber:
            bills = bills.filter(from_organization__classification=chamber)
        if session:
            bills = bills.filter(legislative_session__identifier=session)
        if updated_since:
            bills = bills.filter(updated_at__gte=updated_since)
        if classification:
            bills = bills.filter(classification__contains=[classification])
        if subject:
            bills = bills.filter(subject__contains=[subject])

        bills = optimize(bills, info, [
            '.abstracts',
            '.otherTitles',
            '.otherIdentifiers',
            '.actions',
            '.actions.organization',
            '.actions.relatedEntities',
            '.actions.relatedEntities.organization',
            '.actions.relatedEntities.person',
            '.sponsorships',
            '.documents',
            '.versions',
            '.documents.links',
            '.versions.links',
            '.sources',
            '.relatedBills',
            '.votes',
            '.votes.counts',
            ('.votes.votes', Prefetch('votes__votes',
                                      PersonVote.objects.all().select_related('voter'))),
        ],
            ['.legislativeSession' '.legislativeSession.jurisdiction'],
        )

        return bills

    def resolve_bill(self, info,
                     id=None,
                     jurisdiction=None, session=None, identifier=None,
                     ):
        bill = None

        if jurisdiction and session and identifier:
            query = dict(legislative_session__identifier=session,
                         identifier=identifier)
            query.update(jurisdiction_query(jurisdiction))
            bill = Bill.objects.get(**query)
        if id:
            bill = Bill.objects.get(id=id)

        if not bill:
            raise ValueError("must either pass 'id' or 'jurisdiction', 'session', 'identifier'")

        return bill

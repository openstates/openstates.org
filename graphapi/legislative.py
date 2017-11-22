import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.fields import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from opencivicdata.legislative.models import (
    LegislativeSession,
    Bill, BillAbstract, BillTitle, BillIdentifier, RelatedBill, BillSponsorship,
    BillDocument, BillVersion, BillDocumentLink, BillVersionLink, BillSource,
    BillActionRelatedEntity, BillAction,
    VoteEvent, VoteCount, PersonVote, VoteSource,
)
from .common import OCDNode


class LegislativeSession(DjangoObjectType):
    class Meta:
        model = LegislativeSession
        exclude_fields = ['id']
        filter_fields = {
            'identifier': ['exact'],
            'classification': ['exact'],
        }
        use_connection = True


class BillNode(DjangoObjectType):
    class Meta:
        model = Bill
        interfaces = (OCDNode, )
        filter_fields = {
            'identifier': ['exact'],
        }


class BillAbstractNode(DjangoObjectType):
    class Meta:
        model = BillAbstract
        exclude_fields = ['id', 'bill']


class BillTitleNode(DjangoObjectType):
    class Meta:
        model = BillTitle
        exclude_fields = ['id', 'bill']


class BillIdentifierNode(DjangoObjectType):
    class Meta:
        model = BillIdentifier
        exclude_fields = ['id', 'bill']


class BillSponsorshipNode(DjangoObjectType):
    class Meta:
        model = BillSponsorship
        exclude_fields = ['id', 'bill']


class BillDocumentNode(DjangoObjectType):
    class Meta:
        model = BillDocument
        exclude_fields = ['id', 'bill']


class BillDocumentLinkNode(DjangoObjectType):
    class Meta:
        model = BillDocumentLink
        exclude_fields = ['id', 'document']


class BillVersionNode(DjangoObjectType):
    class Meta:
        model = BillVersion
        exclude_fields = ['id', 'bill']


class BillVersionLinkNode(DjangoObjectType):
    class Meta:
        model = BillVersionLink
        exclude_fields = ['id', 'version']


class BillSourceNode(DjangoObjectType):
    class Meta:
        model = BillSource
        exclude_fields = ['id', 'bill']


class BillActionNode(DjangoObjectType):
    class Meta:
        model = BillAction
        exclude_fields = ['id', 'bill']


class LegislativeQuery:
    bill = graphene.Field(BillNode,
                          id=graphene.String(),
                          jurisdiction=graphene.String(),
                          session=graphene.String(),
                          identifier=graphene.String(),
                          )
    bills = DjangoConnectionField(BillNode,
                                  jurisdiction=graphene.String(),
                                  session=graphene.String(),
                                  chamber=graphene.String(),
                                  updated_since=graphene.String(),
                                  subject=graphene.String(),
                                  classification=graphene.String(),
                                  )

    def resolve_bills(self, info,
                      first=None,
                      jurisdiction=None, chamber=None, session=None,
                      updated_since=None, classification=None,
                      #subject=None,
                      ):
        # bill_id/bill_id__in
        # q (full text)
        # sponsor_id
        # classification
        bills = Bill.objects.all()
        bills = bills.prefetch_related('actions').prefetch_related('legislative_session')
        if jurisdiction:
            bills = bills.filter(legislative_session__jurisdiction__name=jurisdiction)
        if chamber:
            bills = bills.filter(from_organization__classification=chamber)
        if session:
            bills = bills.filter(legislative_session__identifier=session)
        if updated_since:
            bills = bills.filter(updated_at__gte=updated_since)
        if classification:
            bills = bills.filter(classification__contains=[classification])
        # TODO: subject
        # if subject:
        #     bills = bills.filter(
        return bills

    def resolve_bill(self, info,
                     id=None,
                     jurisdiction=None, session=None, identifier=None,
                     # TODO: chamber
                     ):
        bill = None
        if jurisdiction and session and identifier:
            bill = Bill.objects.get(legislative_session__jurisdiction__name=jurisdiction,
                                    legislative_session__identifier=session,
                                    identifier=identifier)
        if id:
            bill = Bill.objects.get(id=id)

        if not bill:
            raise ValueError("must either pass 'id' or 'jurisdiction', 'session', 'identifier'")

        return bill

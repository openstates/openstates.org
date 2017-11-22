import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.fields import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from opencivicdata.core.models import (
    Jurisdiction,
    Organization, OrganizationIdentifier, OrganizationName,
    OrganizationLink, OrganizationSource,
    Person, PersonIdentifier, PersonName, PersonContactDetail, PersonLink,
    PersonSource, Post, Membership,
)
from opencivicdata.legislative.models import (
    LegislativeSession,
    Bill, BillAbstract, BillTitle, BillIdentifier, RelatedBill, BillSponsorship,
    BillDocument, BillVersion, BillDocumentLink, BillVersionLink, BillSource,
    BillActionRelatedEntity, BillAction,
    VoteEvent, VoteCount, PersonVote, VoteSource,
)


# override default ID behavior w/ behavior that preserves OCD ids
class OCDNode(graphene.relay.Node):
    class Meta:
        name = 'Node'

    @staticmethod
    def to_global_id(type, id):
        return id

    @staticmethod
    def get_node_from_global_id(id, info, only_type=None):
        if id.startswith('ocd-jurisdiction'):
            return Jurisdiction.objects.get(id=id)
        elif id.startswith('ocd-organization'):
            return Person.objects.get(id=id)
        elif id.startswith('ocd-person'):
            return Person.objects.get(id=id)
        elif id.startswith('ocd-bill'):
            return Bill.objects.get(id=id)


class PostType(DjangoObjectType):
    class Meta:
        model = Post


class MembershipType(DjangoObjectType):
    class Meta:
        model = Membership


class OrganizationIdentifierType(DjangoObjectType):
    class Meta:
        model = OrganizationIdentifier


class OrganizationNameType(DjangoObjectType):
    class Meta:
        model = OrganizationName


class OrganizationLinkType(DjangoObjectType):
    class Meta:
        model = OrganizationLink


class OrganizationSourceType(DjangoObjectType):
    class Meta:
        model = OrganizationSource


class OrganizationNode(DjangoObjectType):
    class Meta:
        model = Organization
        filter_fields = ['id', 'name', 'classification']
        interfaces = (OCDNode, )


class PersonNode(DjangoObjectType):
    class Meta:
        model = Person
        filter_fields = {
            'name': ['exact', 'istartswith'],
            'id': ['exact'],
        }
        interfaces = (OCDNode, )


class PersonIdentifierType(DjangoObjectType):
    class Meta:
        model = PersonIdentifier


class PersonNameType(DjangoObjectType):
    class Meta:
        model = PersonName


class PersonContactType(DjangoObjectType):
    class Meta:
        model = PersonContactDetail


class PersonLinkType(DjangoObjectType):
    class Meta:
        model = PersonLink


class PersonSourceType(DjangoObjectType):
    class Meta:
        model = PersonSource


class JurisdictionNode(DjangoObjectType):
    class Meta:
        model = Jurisdiction
        interfaces = (OCDNode, )


class LegislativeSession(DjangoObjectType):
    class Meta:
        model = LegislativeSession
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


class BillTitleNode(DjangoObjectType):
    class Meta:
        model = BillTitle


class BillIdentifierNode(DjangoObjectType):
    class Meta:
        model = BillIdentifier


class BillSponsorshipNode(DjangoObjectType):
    class Meta:
        model = BillSponsorship


class BillDocumentNode(DjangoObjectType):
    class Meta:
        model = BillDocument


class BillDocumentLinkNode(DjangoObjectType):
    class Meta:
        model = BillDocumentLink


class BillVersionNode(DjangoObjectType):
    class Meta:
        model = BillVersion


class BillVersionLinkNode(DjangoObjectType):
    class Meta:
        model = BillVersionLink


class BillSourceNode(DjangoObjectType):
    class Meta:
        model = BillSource


class BillActionNode(DjangoObjectType):
    class Meta:
        model = BillAction


class Query(graphene.ObjectType):
    node = graphene.Field(OCDNode, id=graphene.String())

    jurisdiction = graphene.Field(JurisdictionNode,
                                  id=graphene.String(),
                                  name=graphene.String())
    jurisdictions = DjangoConnectionField(JurisdictionNode)
    # TODO: multiple jurisdictions - but how do we ensure they can't
    # traverse deep into bills/etc. from that angle?

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

    legislators = DjangoFilterConnectionField(PersonNode,
                                              latitude=graphene.Float(),
                                              longitude=graphene.Float(),
                                              )
    legislator = graphene.Field(PersonNode)

    organization = graphene.Field(OrganizationNode)

    def resolve_node(self, info, id):
        return OCDNode.get_node_from_global_id(id, info)

    def resolve_jurisdiction(self, info, id=None, name=None):
        if id:
            return Jurisdiction.objects.get(id=id)
        if name:
            return Jurisdiction.objects.get(name=name)
        else:
            raise ValueError("Jurisdiction requires id or name")

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

    def resolve_legislators(self, info,
                            first=None,
                            latitude=None, longitude=None):
        qs = Person.objects.all()

        if latitude and longitude:
            qs = qs.filter(name__startswith='Y')

        return qs


schema = graphene.Schema(query=Query)

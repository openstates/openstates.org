import graphene
from graphene_django.types import DjangoObjectType
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

    bill = graphene.Field(BillNode,
                          id=graphene.String(),
                          jurisdiction=graphene.String(),
                          session=graphene.String(),
                          )

    legislators = DjangoFilterConnectionField(PersonNode,
                                              latitude=graphene.Float(),
                                              longitude=graphene.Float(),
                                              )

    def resolve_node(self, info, id):
        return OCDNode.get_node_from_global_id(id, info)

    def resolve_jurisdiction(self, info, id=None, name=None):
        if id:
            return Jurisdiction.objects.get(id=id)
        if name:
            return Jurisdiction.objects.get(name=name)
        else:
            raise ValueError("Jurisdiction requires id or name")

    def resolve_legislators(self, info,
                            first=None,
                            latitude=None, longitude=None):
        qs = Person.objects.all()

        if latitude and longitude:
            qs = qs.filter(name__startswith='Y')

        return qs


schema = graphene.Schema(query=Query)

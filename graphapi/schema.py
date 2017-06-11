from graphene_django import DjangoObjectType
import graphene
from graphene_django.filter import DjangoFilterConnectionField
from opencivicdata.core.models import (
    Jurisdiction,
    Organization, OrganizationIdentifier, OrganizationName,
    OrganizationLink, OrganizationSource,
    Person, PersonIdentifier, PersonName, PersonContactDetail, PersonLink,
    PersonSource,
    Post, Membership,
    # currently not supporting
    # (Post|Membership|Organization)(ContactDetail|Link)
)


# override default ID behavior w/ behavior that preserves
# OCD ids
class OCDNode(graphene.relay.Node):
    class Meta:
        name = 'Node'

    @staticmethod
    def to_global_id(type, id):
        return id

    @staticmethod
    def get_node_from_global_id(id, context, info, only_type=None):
        if id.startswith('ocd-jurisdiction'):
            return Jurisdiction.objects.get(id=id)
        elif id.startswith('ocd-organization'):
            return Person.objects.get(id=id)
        elif id.startswith('ocd-person'):
            return Person.objects.get(id=id)


class JurisdictionNode(DjangoObjectType):
    class Meta:
        model = Jurisdiction
        filter_fields = ['id', 'name', 'classification']
        interfaces = (OCDNode, )


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
        filter_fields = ['id', 'name']
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


class Query(graphene.ObjectType):
    jurisdiction = OCDNode.Field(JurisdictionNode)
    all_jurisdictions = DjangoFilterConnectionField(JurisdictionNode)
    organization = OCDNode.Field(OrganizationNode)
    all_organizations = DjangoFilterConnectionField(OrganizationNode)
    person = OCDNode.Field(PersonNode)
    all_people = DjangoFilterConnectionField(PersonNode)


schema = graphene.Schema(query=Query)

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
from .common import OCDNode


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


class CoreQuery:
    jurisdiction = graphene.Field(JurisdictionNode,
                                  id=graphene.String(),
                                  name=graphene.String())
    jurisdictions = DjangoConnectionField(JurisdictionNode)
    # TODO: multiple jurisdictions - but how do we ensure they can't
    # traverse deep into bills/etc. from that angle?

    legislators = DjangoFilterConnectionField(PersonNode,
                                              latitude=graphene.Float(),
                                              longitude=graphene.Float(),
                                              )
    legislator = graphene.Field(PersonNode)

    organization = graphene.Field(OrganizationNode)

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

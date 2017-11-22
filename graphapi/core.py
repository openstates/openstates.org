import datetime
from django.db.models import Q
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
        filter_fields = []
        interfaces = (OCDNode, )

    current_memberships = graphene.List(MembershipType,
                                        classification=graphene.List(graphene.String)
                                        )

    def resolve_current_memberships(self, info, classification=None):
        today = datetime.date.today().isoformat()
        qs = self.memberships.filter(Q(start_date='') | Q(start_date__lte=today),
                                     Q(end_date='') | Q(end_date__gte=today))
        if classification:
            qs = qs.filter(organization__classification__in=classification)
        return qs


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

    people = DjangoFilterConnectionField(PersonNode,
                                         member_of=graphene.String(),
                                         ever_member_of=graphene.String(),
                                         chamber=graphene.String(),
                                         district=graphene.String(),
                                         name=graphene.String(),
                                         party=graphene.String(),
                                         latitude=graphene.Float(),
                                         longitude=graphene.Float(),
                                         )
    person = graphene.Field(PersonNode)


    organization = graphene.Field(OrganizationNode)

    def resolve_jurisdiction(self, info, id=None, name=None):
        if id:
            return Jurisdiction.objects.get(id=id)
        if name:
            return Jurisdiction.objects.get(name=name)
        else:
            raise ValueError("Jurisdiction requires id or name")

    def resolve_people(self, info,
                       first=None,
                       member_of=None, ever_member_of=None,
                       district=None, name=None, party=None,
                       latitude=None, longitude=None,
                       ):
        qs = Person.objects.all()

        if name:
            qs = qs.filter(Q(name__icontains=name) |
                           Q(other_names__name__icontains=name)
                           )
        if member_of:
            qs = qs.member_of(member_of)
        if ever_member_of:
            qs = qs.member_of(ever_member_of, current_only=False)

        # TODO: district

        if party:
            qs = qs.member_of(party)

        if latitude and longitude:
            try:
                # TODO: limit to current
                qs = qs.filter(
                    memberships__post__division__geometries__boundary__shape__contains=(
                        'POINT({} {})'.format(longitude, latitude)
                    )
                )
            except ValueError:
                raise ValueError('invalid lat or lon')
        elif latitude or longitude:
            raise ValueError('must provide lat & lon together')

        return qs

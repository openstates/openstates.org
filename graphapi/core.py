import datetime
import graphene
from django.db.models import Q, Prefetch
from opencivicdata.core.models import Jurisdiction, Organization, Person, Membership
from .common import OCDBaseNode, IdentifierNode, NameNode, LinkNode
from .optimization import optimize


def _resolve_suborganizations(root_obj, field_name, classification=None):
    """ resolve organizations by classification optionally using the prefetch cache """

    # special case filtering if organizations are prefetched
    if classification and field_name in getattr(root_obj, '_prefetched_objects_cache', []):
        return [o for o in root_obj._prefetched_objects_cache[field_name]
                if o.classification == classification]

    qs = getattr(root_obj, field_name).all()

    if classification:
        qs = qs.filter(classification=classification)

    return qs


def _current_membership_filter(qs, info, classification=None, prefix=None):
    today = datetime.date.today().isoformat()
    qs = qs.filter(Q(start_date='') | Q(start_date__lte=today),
                   Q(end_date='') | Q(end_date__gte=today))
    if classification:
        qs = qs.filter(organization__classification__in=classification)

    # if we're getting a membership we're probably going to need org/post
    qs = optimize(qs, info, None, ['.organization', '.post', '.post.division'], prefix=prefix)
    return qs


class ContactDetailNode(graphene.ObjectType):
    type = graphene.String()
    value = graphene.String()
    note = graphene.String()
    label = graphene.String()


class OrganizationNode(OCDBaseNode):
    name = graphene.String()
    image = graphene.String()
    # jurisdiction left out for now since traversing up can lead to query explosion
    classification = graphene.String()
    founding_date = graphene.String()
    dissolution_date = graphene.String()

    # self-referential relationship
    parent = graphene.Field('graphapi.core.OrganizationNode')
    # children = graphene.List('graphapi.core.OrganizationNode')
    children = graphene.relay.ConnectionField('graphapi.core.OrganizationConnection',
                                              classification=graphene.String())

    # related objects
    identifiers = graphene.List(IdentifierNode)
    other_names = graphene.List(NameNode)
    links = graphene.List(LinkNode)
    sources = graphene.List(LinkNode)

    def resolve_children(self, info, classification=None):
        return _resolve_suborganizations(self, 'children', classification)

    def resolve_identifiers(self, info):
        return self.identifiers.all()

    def resolve_other_names(self, info):
        return self.other_names.all()

    def resolve_links(self, info):
        return self.links.all()

    def resolve_sources(self, info):
        return self.sources.all()


class DivisionNode(OCDBaseNode):
    name = graphene.String()
    redirect = graphene.Field('graphapi.core.DivisionNode')
    country = graphene.String()


class PostNode(OCDBaseNode):
    label = graphene.String()
    role = graphene.String()
    division = graphene.Field(DivisionNode)
    start_date = graphene.String()
    end_date = graphene.String()
    maximum_memberships = graphene.String()

    # organization excluded from this direction
    # contact_details and links not used


class PersonNode(OCDBaseNode):
    name = graphene.String()
    sort_name = graphene.String()
    family_name = graphene.String()
    given_name = graphene.String()
    image = graphene.String()
    # not used: gender, summary, national_identity, biography
    birth_date = graphene.String()
    death_date = graphene.String()

    # related objects
    identifiers = graphene.List(IdentifierNode)
    other_names = graphene.List(NameNode)
    links = graphene.List(LinkNode)
    sources = graphene.List(LinkNode)
    contact_details = graphene.List(ContactDetailNode)

    # special attributes
    current_memberships = graphene.List('graphapi.core.MembershipNode',
                                        classification=graphene.List(graphene.String)
                                        )

    def resolve_identifiers(self, info):
        return self.identifiers.all()

    def resolve_other_names(self, info):
        return self.other_names.all()

    def resolve_links(self, info):
        return self.links.all()

    def resolve_sources(self, info):
        return self.sources.all()

    def resolve_contact_details(self, info):
        return self.contact_details.all()

    def resolve_current_memberships(self, info, classification=None):
        if hasattr(self, 'current_memberships'):
            return self.current_memberships
        else:
            return _current_membership_filter(self.memberships, info, classification)


class MembershipNode(OCDBaseNode):
    organization = graphene.Field(OrganizationNode)
    person = graphene.Field(PersonNode)
    person_name = graphene.String()
    post = graphene.Field(PostNode)
    # on_behalf_of  (not used?)
    label = graphene.String()
    role = graphene.String()
    start_date = graphene.String()
    end_date = graphene.String()

    # contact_details and links not used


class LegislativeSessionNode(graphene.ObjectType):
    jurisdiction = graphene.Field('graphapi.core.JurisdictionNode')
    identifier = graphene.String()
    name = graphene.String()
    classification = graphene.String()
    start_date = graphene.String()
    end_date = graphene.String()


class LegislativeSessionConnection(graphene.relay.Connection):
    class Meta:
        node = LegislativeSessionNode


class OrganizationConnection(graphene.relay.Connection):
    class Meta:
        node = OrganizationNode


class JurisdictionNode(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    url = graphene.String()
    classification = graphene.String()
    feature_flags = graphene.List(graphene.String)

    legislative_sessions = graphene.relay.ConnectionField(LegislativeSessionConnection)
    organizations = graphene.relay.ConnectionField(OrganizationConnection,
                                                   classification=graphene.String())

    def resolve_legislative_sessions(self, info,
                                     first=None, last=None, before=None, after=None):
        return self.legislative_sessions.all()

    def resolve_organizations(self, info,
                              first=None, last=None, before=None, after=None,
                              classification=None):
        return _resolve_suborganizations(self, 'organizations', classification)


class JurisdictionConnection(graphene.relay.Connection):
    class Meta:
        node = JurisdictionNode


class PersonConnection(graphene.relay.Connection):
    class Meta:
        node = PersonNode


class CoreQuery:
    jurisdictions = graphene.relay.ConnectionField(JurisdictionConnection)
    jurisdiction = graphene.Field(JurisdictionNode,
                                  id=graphene.String(),
                                  name=graphene.String())
    people = graphene.relay.ConnectionField(PersonConnection,
                                            member_of=graphene.String(),
                                            ever_member_of=graphene.String(),
                                            chamber=graphene.String(),
                                            district=graphene.String(),
                                            name=graphene.String(),
                                            party=graphene.String(),
                                            latitude=graphene.Float(),
                                            longitude=graphene.Float(),
                                            )
    person = graphene.Field(PersonNode, id=graphene.ID())
    organization = graphene.Field(OrganizationNode, id=graphene.ID())

    def resolve_jurisdictions(self, info):
        qs = Jurisdiction.objects.all()
        return optimize(qs, info,
                        ['.legislativeSessions',
                         '.organizations',
                         '.organizations.children'])

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
            qs = qs.member_of(member_of, post=district)
        if ever_member_of:
            qs = qs.member_of(ever_member_of, current_only=False, post=district)
        if district and not (member_of or ever_member_of):
            raise ValueError("'district' parameter requires specifying either "
                             "'memberOf' or 'everMemberOf'")

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

        qs = optimize(qs, info, [
            '.identifiers',
            '.otherNames',
            '.links',
            '.sources',
            '.contactDetails',
            ('.currentMemberships',
             Prefetch('memberships',
                      queryset=_current_membership_filter(Membership.objects, info,
                                                          prefix='.currentMemberships'),
                      to_attr='current_memberships')),
        ])

        return qs

    def resolve_person(self, info, id):
        return Person.objects.get(pk=id)

    def resolve_organization(self, info, id):
        return optimize(Organization.objects, info, None, ['.parent']).get(pk=id)

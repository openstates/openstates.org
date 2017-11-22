import graphene
from opencivicdata.core.models import Jurisdiction, Person, Organization
from opencivicdata.legislative.models import Bill


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
            return Organization.objects.get(id=id)
        elif id.startswith('ocd-person'):
            return Person.objects.get(id=id)
        elif id.startswith('ocd-bill'):
            return Bill.objects.get(id=id)

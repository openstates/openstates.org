import graphene
from .common import OCDNode
from .legislative import LegislativeQuery
from .core import CoreQuery


class Query(LegislativeQuery, CoreQuery, graphene.ObjectType):
    node = graphene.Field(OCDNode, id=graphene.String())

    def resolve_node(self, info, id):
        return OCDNode.get_node_from_global_id(id, info)


schema = graphene.Schema(query=Query)

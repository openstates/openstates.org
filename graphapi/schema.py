import graphene
from .legislative import LegislativeQuery
from .core import CoreQuery


class Query(LegislativeQuery, CoreQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)

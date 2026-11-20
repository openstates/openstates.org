import graphene

from .core import CoreQuery
from .legislative import LegislativeQuery


class Query(LegislativeQuery, CoreQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)

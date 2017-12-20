import graphene
from collections import Iterable
from graphql_relay.connection.arrayconnection import connection_from_list_slice


class OCDBaseNode(graphene.ObjectType):
    id = graphene.String()
    created_at = graphene.String()
    updated_at = graphene.String()
    extras = graphene.String()


class IdentifierNode(graphene.ObjectType):
    identifier = graphene.String()
    scheme = graphene.String()


class LinkNode(graphene.ObjectType):
    note = graphene.String()
    url = graphene.String()


class NameNode(graphene.ObjectType):
    name = graphene.String()
    note = graphene.String()
    start_date = graphene.String()
    end_date = graphene.String()


class DjangoConnectionField(graphene.relay.ConnectionField):
    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if isinstance(resolved, connection_type):
            return resolved

        if not isinstance(resolved, Iterable):
            raise AssertionError('Resolved value from the connection field have to be '
                                 'iterable or instance of {}. Received "{}"'
                                 ).format(connection_type, type(resolved))

        total_size = args.get('first') or args.get('last')
        # if not total_size or total_size > 100:
        #     raise ValueError('must specify a first/last parameter <= 100')

        if isinstance(resolved, list):
            _len = len(resolved)
        else:
            # Django QuerySet
            _len = resolved.count()

        connection = connection_from_list_slice(
            list_slice=resolved,
            args=args,
            connection_type=connection_type,
            edge_type=connection_type.Edge,
            pageinfo_type=graphene.relay.PageInfo,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
        )
        connection.iterable = resolved
        return connection

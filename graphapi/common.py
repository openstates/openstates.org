import graphene


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

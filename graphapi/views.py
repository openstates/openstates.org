from graphene_django.views import GraphQLView
from profiles.verifier import verify_request

GraphQLView.graphiql_template = "graphene_graphiql_explorer/graphiql.html"


class KeyedGraphQLView(GraphQLView):
    def get_response(self, request, data, show_graphiql=False):
        internal = request.get_host() in request.META.get("HTTP_ORIGIN", "")

        # check key only if we're not handling a graphiql request
        if not show_graphiql and not internal:
            error = verify_request(request, "v2")
            if error:
                return error, error.status_code

        return super().get_response(request, data, show_graphiql)

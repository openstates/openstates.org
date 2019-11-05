from simplekeys.verifier import verify_request
from graphene_django.views import GraphQLView
from django.conf import settings
import newrelic


class KeyedGraphQLView(GraphQLView):
    graphiql_template = "graphene/graphiql-keyed.html"

    def get_response(self, request, data, show_graphiql=False):
        # check key only if we're not handling a graphiql request
        if not show_graphiql:
            newrelic.agent.add_custom_parameter(
                "key",
                request.META.get(
                    getattr(settings, "SIMPLEKEYS_HEADER", "HTTP_X_API_KEY")
                ),
            )
            newrelic.agent.add_custom_parameter("request-data", data)
            error = verify_request(request, "graphapi")
            if error:
                return error, error.status_code

        return super().get_response(request, data, show_graphiql)

    def render_graphiql(self, request, **data):
        data["demo_key"] = settings.GRAPHQL_DEMO_KEY
        return super().render_graphiql(request, **data)

from simplekeys.verifier import verify_request
from graphene_django.views import GraphQLView
from django.conf import settings


class KeyedGraphQLView(GraphQLView):
    graphiql_template = "graphene/graphiql-keyed.html"

    def get_response(self, request, data, show_graphiql=False):
        # check key only if we're not handling a graphiql request
        # if not show_graphiql:
        #     error = verify_request(request, 'graphapi')
        #     if error:
        #         print('graphapi/views: get_response bailed ')
        #         return error, error.status_code

        return super().get_response(request, data, show_graphiql)

    def render_graphiql(self, request, **data):
        data['demo_key'] = settings.GRAPHQL_DEMO_KEY
        return super().render_graphiql(request, **data)

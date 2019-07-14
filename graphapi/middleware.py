import logging
from graphql.language.ast import FragmentSpread


class QueryCostException(Exception):
    pass


log = logging.getLogger('graphapi')


def _get_counts(info, fragments, args={}):
    multiplier = 1
    inner_multiplier = 0

    if isinstance(info, FragmentSpread):
        for selection in fragments[info.name.value].selection_set.selections:
            inner_multiplier += _get_counts(selection, fragments)
    else:
        # the multiplier is either 1 or the number of elements returned
        multiplier = args.get('first', args.get('last', 1))

        # count up how many multi-nodes inside
        if info.selection_set:
            for selection in info.selection_set.selections:
                inner_multiplier += _get_counts(selection, fragments)

    # if this wasn't a multi-node, this counts as one node
    if inner_multiplier == 0:
        inner_multiplier = 1

    return multiplier * inner_multiplier


class QueryProtectionMiddleware(object):
    def __init__(self, max_cost=5000):
        self.max_cost = max_cost

    def resolve(self, next, root, info, **args):
        if root is None:
            count = _get_counts(info.field_asts[0], info.fragments, args)
            log.debug(f'graphql query name={info.field_name} asts={info.field_asts} cost={count}')
            if count > self.max_cost:
                raise QueryCostException(
                    f'Query Cost is too high ({count}), limit is {self.max_cost}'
                )
        return next(root, info, **args)

from .optimization import get_field_names

def _get_counts(info):
    multiplier = 0
    for argument in info.arguments:
        if argument.name.value in ('first', 'last'):
            multiplier = int(argument.value.value)

    inner_multiplier = 1
    if info.selection_set:
        for selection in info.selection_set.selections:
            # if isinstance(selection, FragmentSpread):
            #     return 1
            #     # yield from _yield_counts(info.fragments[selection.name.value].selection_set)
            # else:
            # multiplier *= _get_counts(selection)
            inner_multiplier += _get_counts(selection)

    print(info.name, multiplier, inner_multiplier)

    return multiplier * inner_multiplier


class QueryProtectionMiddleware(object):
    def resolve(self, next, root, info, **args):
        if root is None:
            print(_get_counts(info.field_asts[0]))
        return next(root, info, **args)

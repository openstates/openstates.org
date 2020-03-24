import re
from graphql.language.ast import FragmentSpread


def _to_snake(word):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", word)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def transform_path(path):
    pieces = path.split(".")
    if pieces[0] != "":
        raise ValueError("field path must start with .")

    return "__".join(_to_snake(piece) for piece in pieces[1:])


def get_field_names(info):
    # info.operation has the entire operation, could be used for
    # cross-query optimization potentially
    return list(
        _yield_field_names(info.field_asts[0].selection_set, "", info.fragments)
    )


def _yield_field_names(selection_set, prefix, fragments):
    if not selection_set:
        return

    for selection in selection_set.selections:
        if isinstance(selection, FragmentSpread):
            yield from _yield_field_names(
                fragments[selection.name.value].selection_set, prefix, fragments
            )
        else:
            # normal handling for Field selections
            if selection.name.value not in ("edges", "node"):
                yield prefix + "." + selection.name.value
                new_prefix = prefix + "." + selection.name.value
                yield from _yield_field_names(
                    selection.selection_set, new_prefix, fragments
                )
            else:
                yield from _yield_field_names(
                    selection.selection_set, prefix, fragments
                )


def optimize(queryset, info, prefetch, select_related=None, *, prefix=None):
    to_prefetch = set()
    to_select = set()
    field_names = get_field_names(info)

    # only take fields that are within prefix (used for Prefetch() sub-field optimization)
    if prefix:
        field_names = [
            fn.replace(prefix, "") for fn in field_names if fn.startswith(prefix)
        ]

    if prefetch:
        for field in prefetch:
            if isinstance(field, tuple):
                field, prefetch_name = field
                if field in field_names:
                    to_prefetch.add(prefetch_name)
            elif isinstance(field, str):
                if field in field_names:
                    to_prefetch.add(transform_path(field))
        queryset = queryset.prefetch_related(*to_prefetch)

    if select_related:
        for field in select_related:
            if field in field_names:
                to_select.add(transform_path(field))
        queryset = queryset.select_related(*to_select)

    return queryset

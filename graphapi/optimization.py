

def get_field_names(info):
    # info.operation has the entire operation, could be used for
    # cross-query optimization potentially
    return list(_yield_field_names(info.field_asts[0].selection_set,
                                   ''))
    # info.field_asts[0].name.value))


def _yield_field_names(selection_set, prefix):
    if not selection_set:
        return
    for selection in selection_set.selections:
        if selection.name.value not in ('edges', 'node'):
            yield prefix + '.' + selection.name.value
            new_prefix = prefix + '.' + selection.name.value
            yield from _yield_field_names(selection.selection_set, new_prefix)
        else:
            yield from _yield_field_names(selection.selection_set, prefix)


def optimize(queryset, info, prefetch, select_related=None):
    to_prefetch = set()
    to_select = set()
    field_names = get_field_names(info)

    for field, prefetch in prefetch.items():
        if field in field_names:
            to_prefetch.add(prefetch)

    print('prefetching', to_prefetch)

    if select_related:
        for field, select in select_related.items():
            if field in field_names:
                to_select.add(select)
        queryset = queryset.select_related(*to_select)

    queryset = queryset.prefetch_related(*to_prefetch)
    return queryset

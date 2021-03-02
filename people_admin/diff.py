"""
Generic tools for representing object differences in an easy to apply way.

Diffs will be stored in the format:
    [key, action, param]

key should be a complete dotted path to a given property, e.g.:
    - last_name
    - other_identifiers.2
    - ids.twitter

action should be one of:
    - set: obj[key] = param
    - append: obj[key].append(param)
    - delete: obj.pop(key)      // param is not used
"""
import typing
from dataclasses import dataclass


@dataclass
class DiffItem:
    action: str
    key: str
    param: typing.Optional[str]


def apply_diff(obj, diff):
    for item in diff:
        obj = apply_diff_item(obj, diff)


def get_subobj(obj: dict, key_pieces: typing.List[str]):
    if key_pieces:
        k = key_pieces[0]
        if isinstance(obj, list):
            k = int(k)
        return get_subobj(obj[k], key_pieces[1:])
    return obj


def apply_diff_item(obj, diff_item):
    diff_item = DiffItem(*diff_item)
    key_pieces = diff_item.key.split(".")

    if diff_item.action == "set":
        subobj = get_subobj(obj, key_pieces[:-1])
        k = key_pieces[-1]
        if isinstance(subobj, list):
            k = int(k)
        subobj[k] = diff_item.param

    return obj

import pytest
from ..diff import apply_diff_item


@pytest.mark.parametrize(
    "start,patch,output",
    [
        # set new value
        ({}, ["set", "a", 123], {"a": 123}),
        ({}, ["set", "a", {"b": "c"}], {"a": {"b": "c"}}),
        # replace value
        ({"a": 4}, ["set", "a", 123], {"a": 123}),
        ({"a": 4}, ["set", "a", {"b": "c"}], {"a": {"b": "c"}}),
        # set multiple levels deep
        ({"a": {"b": 0}}, ["set", "a.b", 123], {"a": {"b": 123}}),
        # set within a list
        ({"a": [1, 0, 3]}, ["set", "a.1", 2], {"a": [1, 2, 3]}),
        (
            {"a": [{"i": 1}, {"ii": 0}, {"iii": 3}]},
            ["set", "a.1.ii", 2],
            {"a": [{"i": 1}, {"ii": 2}, {"iii": 3}]},
        ),
    ],
)
def test_set_item(start, patch, output):
    assert apply_diff_item(start, patch) == output

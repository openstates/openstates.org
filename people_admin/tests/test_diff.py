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


@pytest.mark.parametrize(
    "start,patch,output",
    [
        ({"a": []}, ["append", "a", 123], {"a": [123]}),
        ({"a": {"b": [1, 2, 3]}}, ["append", "a.b", 4], {"a": {"b": [1, 2, 3, 4]}}),
        (
            {"a": [{"i": 1}, {"ii": 2}, {"iii": 3}]},
            ["append", "a", {"iv": 4}],
            {"a": [{"i": 1}, {"ii": 2}, {"iii": 3}, {"iv": 4}]},
        ),
        # append should create list if not present
        ({}, ["append", "a", 123], {"a": [123]}),
    ],
)
def test_append_item(start, patch, output):
    assert apply_diff_item(start, patch) == output


@pytest.mark.parametrize(
    "start,patch,output",
    [
        ({"a": [1, 2, 3]}, ["delete", "a", None], {}),
        ({"a": [1, 2, 3]}, ["delete", "a.1", None], {"a": [1, 3]}),
        ({"a": {"b": {"c": "d"}}}, ["delete", "a.b.c", None], {"a": {"b": {}}}),
    ],
)
def test_delete_item(start, patch, output):
    assert apply_diff_item(start, patch) == output

from ..optimization import transform_path


def test_transform_path():
    examples = [
        ('.oneword', 'oneword'),
        ('.twoWords', 'two_words'),
        ('.dotted.path', 'dotted__path'),
        ('.moreComplex.example.ofThis', 'more_complex__example__of_this'),
    ]

    for input, output in examples:
        assert transform_path(input) == output

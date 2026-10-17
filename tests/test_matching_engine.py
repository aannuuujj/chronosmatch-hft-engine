from chronosmatch.matching_engine import match_quantity


def test_matching_crossing_orders():
    assert match_quantity(101, 100, 5, 3) == 3


def test_matching_non_crossing_orders():
    assert match_quantity(99, 100, 5, 3) == 0


def test_matching_partial_quantity():
    assert match_quantity(100, 100, 2, 7) == 2


def test_matching_empty_quantity():
    assert match_quantity(100, 100, 0, 7) == 0

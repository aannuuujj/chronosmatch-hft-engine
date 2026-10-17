from chronosmatch.matching_engine import match_quantity


def test_matching_crossing_orders():
    assert match_quantity(101, 100, 5, 3) == 3


def test_matching_non_crossing_orders():
    assert match_quantity(99, 100, 5, 3) == 0


def test_matching_partial_quantity():
    assert match_quantity(100, 100, 2, 7) == 2


def test_matching_empty_quantity():
    assert match_quantity(100, 100, 0, 7) == 0


def test_cython_order_book_matches_orders():
    from chronosmatch.matching_engine import CythonOrderBook

    book = CythonOrderBook()
    assert book.add_order(1, 1, 100, 5, 1) == []
    trades = book.add_order(2, 0, 100, 3, 2)

    assert len(trades) == 1
    assert trades[0]["price"] == 100
    assert trades[0]["quantity"] == 3
    assert trades[0]["buy_order_id"] == 2
    assert trades[0]["sell_order_id"] == 1
    assert book.get_trade_count() == 1


def test_cython_order_book_price_priority():
    from chronosmatch.matching_engine import CythonOrderBook

    book = CythonOrderBook()
    book.add_order(1, 1, 101, 2, 1)
    book.add_order(2, 1, 100, 2, 2)

    trades = book.add_order(3, 0, 101, 2, 3)

    assert len(trades) == 1
    assert trades[0]["sell_order_id"] == 2
    assert trades[0]["price"] == 100

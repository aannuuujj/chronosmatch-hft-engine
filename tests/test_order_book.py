from chronosmatch.order_book import Order, OrderBook


def test_buy_and_sell_orders_match():
    book = OrderBook()

    book.add_order(Order(1, "SELL", 100, 5, 1))
    book.add_order(Order(2, "BUY", 100, 3, 2))

    assert len(book.trades) == 1
    assert book.trades[0]["price"] == 100
    assert book.trades[0]["quantity"] == 3
    assert book.asks[100][0].quantity == 2
def test_price_time_priority():
    book = OrderBook()

    # Two sell orders at the same price
    book.add_order(Order(1, "SELL", 100, 2, 1))
    book.add_order(Order(2, "SELL", 100, 3, 2))

    # Buy 3 units: oldest sell order must execute first
    book.add_order(Order(3, "BUY", 100, 3, 3))

    assert len(book.trades) == 2
    assert book.trades[0]["sell_order_id"] == 1
    assert book.trades[0]["quantity"] == 2
    assert book.trades[1]["sell_order_id"] == 2
    assert book.trades[1]["quantity"] == 1
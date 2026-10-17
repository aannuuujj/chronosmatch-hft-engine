from chronosmatch.order_book import Order, OrderBook


def test_buy_and_sell_orders_match():
    book = OrderBook()

    book.add_order(Order(1, "SELL", 100, 5, 1))
    book.add_order(Order(2, "BUY", 100, 3, 2))

    assert len(book.trades) == 1
    assert book.trades[0]["price"] == 100
    assert book.trades[0]["quantity"] == 3
    assert book.asks[100][0].quantity == 2

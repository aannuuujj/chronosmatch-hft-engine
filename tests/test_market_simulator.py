import asyncio

from chronosmatch.market_simulator import generate_orders, run_simulation


def test_simulator_generates_requested_order_count():
    async def check():
        orders = [order async for order in generate_orders(100)]
        assert len(orders) == 100
        assert all(order.quantity > 0 for order in orders)

    asyncio.run(check())


def test_simulation_processes_orders():
    book = asyncio.run(run_simulation(100))
    traded_quantity = sum(trade["quantity"] for trade in book.trades)

    assert len(book.trades) > 0
    assert traded_quantity > 0

"""Asynchronous market simulator for ChronosMatch."""

import asyncio
import random
from collections.abc import AsyncIterator

from chronosmatch.order_book import Order, OrderBook


async def generate_orders(
    count: int = 100,
    seed: int = 42,
) -> AsyncIterator[Order]:
    """Generate reproducible mock buy and sell orders."""
    rng = random.Random(seed)

    for order_id in range(1, count + 1):
        side = rng.choice(("BUY", "SELL"))
        price = rng.randint(98, 102)
        quantity = rng.randint(1, 10)

        yield Order(
            order_id=order_id,
            side=side,
            price=price,
            quantity=quantity,
            timestamp=order_id,
        )

        await asyncio.sleep(0)


async def run_simulation(count: int = 100) -> OrderBook:
    """Feed generated orders into the matching engine."""
    book = OrderBook()

    async for order in generate_orders(count):
        book.add_order(order)

    return book


async def main() -> None:
    book = await run_simulation(100)

    print("ChronosMatch Market Simulation")
    print("------------------------------")
    print(f"Orders processed: 100")
    print(f"Trades executed:  {len(book.trades)}")
    print(f"Remaining bids:   {sum(map(len, book.bids.values()))}")
    print(f"Remaining asks:   {sum(map(len, book.asks.values()))}")


if __name__ == "__main__":
    asyncio.run(main())

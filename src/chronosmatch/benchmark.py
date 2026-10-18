"""Latency benchmark for the ChronosMatch Python order book."""

import asyncio
import statistics
import time

from chronosmatch.market_simulator import generate_orders
from chronosmatch.order_book import OrderBook


async def benchmark(order_count: int = 10_000) -> None:
    book = OrderBook()
    latencies_ns = []

    async for order in generate_orders(order_count):
        start = time.perf_counter_ns()
        book.add_order(order)
        latencies_ns.append(time.perf_counter_ns() - start)

    ordered = sorted(latencies_ns)
    p99_index = min(len(ordered) - 1, int(len(ordered) * 0.99))

    print("ChronosMatch Latency Benchmark")
    print("------------------------------")
    print(f"Orders processed: {len(latencies_ns):,}")
    print(f"Trades executed:  {len(book.trades):,}")
    print(f"Mean latency:     {statistics.mean(latencies_ns):,.0f} ns")
    print(f"Median latency:   {statistics.median(latencies_ns):,.0f} ns")
    print(f"P99 latency:      {ordered[p99_index]:,} ns")
    print(f"Max latency:      {max(latencies_ns):,} ns")


if __name__ == "__main__":
    asyncio.run(benchmark())

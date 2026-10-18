"""Repeated Python vs Cython order-book benchmark."""

import asyncio
import statistics
import time
from dataclasses import replace

from chronosmatch.market_simulator import generate_orders
from chronosmatch.order_book import OrderBook
from chronosmatch.matching_engine import CythonOrderBook


def measure_python(orders):
    book = OrderBook()
    latencies = []

    for original in orders:
        order = replace(original)
        start = time.perf_counter_ns()
        book.add_order(order)
        latencies.append(time.perf_counter_ns() - start)

    return latencies, len(book.trades)


def measure_cython(orders):
    book = CythonOrderBook()
    latencies = []

    for order in orders:
        start = time.perf_counter_ns()
        book.add_order(
            order.order_id,
            0 if order.side == "BUY" else 1,
            order.price,
            order.quantity,
            order.timestamp,
        )
        latencies.append(time.perf_counter_ns() - start)

    return latencies, book.get_trade_count()


def summarize(values):
    ordered = sorted(values)
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "p99": ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))],
        "max": max(values),
    }


async def main(order_count: int = 10_000, rounds: int = 5):
    orders = [
        order async for order in generate_orders(order_count, seed=42)
    ]

    results = {"Python": [], "Cython": []}

    # Warm up the compiled extension before collecting measurements.
    warmup = orders[:min(500, len(orders))]
    measure_python(warmup)
    measure_cython(warmup)

    for run in range(1, rounds + 1):
        # Alternate order to reduce systematic first-run bias.
        if run % 2:
            python_result = measure_python(orders)
            cython_result = measure_cython(orders)
        else:
            cython_result = measure_cython(orders)
            python_result = measure_python(orders)

        python_latencies, python_trades = python_result
        cython_latencies, cython_trades = cython_result

        if python_trades != cython_trades:
            raise RuntimeError(
                f"Trade count mismatch: Python={python_trades}, "
                f"Cython={cython_trades}"
            )

        results["Python"].append(summarize(python_latencies))
        results["Cython"].append(summarize(cython_latencies))

        print(
            f"Round {run}/{rounds}: "
            f"Python median={statistics.median(python_latencies):,.0f} ns | "
            f"Cython median={statistics.median(cython_latencies):,.0f} ns | "
            f"Trades={python_trades:,}"
        )

    print("\nSummary: median of each round's median latency")
    print("---------------------------------------------")

    for name, runs in results.items():
        print(f"\n{name}")
        for metric in ("mean", "median", "p99", "max"):
            values = [run[metric] for run in runs]
            print(f"{metric.capitalize():<8}: {statistics.median(values):,.0f} ns")

    python_median = statistics.median(
        run["median"] for run in results["Python"]
    )
    cython_median = statistics.median(
        run["median"] for run in results["Cython"]
    )

    improvement = (python_median - cython_median) / python_median * 100
    print(f"\nMedian-latency improvement: {improvement:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())

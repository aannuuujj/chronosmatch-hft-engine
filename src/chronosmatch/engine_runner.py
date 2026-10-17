"""Connect the shared-memory ring buffer to the Cython matching engine."""

from chronosmatch.matching_engine import CythonOrderBook
from chronosmatch.shared_memory import SharedMemoryRingBuffer


def process_pending_orders(
    buffer: SharedMemoryRingBuffer,
    book: CythonOrderBook,
) -> int:
    """Process all currently available orders; return the number processed."""
    processed = 0

    while True:
        order = buffer.get()
        if order is None:
            break

        order_id, side, price, quantity, timestamp = order
        book.add_order(order_id, side, price, quantity, timestamp)
        processed += 1

    return processed

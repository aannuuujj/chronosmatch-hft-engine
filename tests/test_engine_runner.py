import tempfile
from pathlib import Path

from chronosmatch.engine_runner import process_pending_orders
from chronosmatch.matching_engine import CythonOrderBook
from chronosmatch.shared_memory import SharedMemoryRingBuffer


def test_process_pending_orders_matches_trade():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "orders.mmap")

        with SharedMemoryRingBuffer(path, capacity=8) as buffer:
            book = CythonOrderBook()

            assert buffer.put(1, 1, 100, 5, 1)
            assert buffer.put(2, 0, 100, 3, 2)

            processed = process_pending_orders(buffer, book)

            assert processed == 2
            assert book.get_trade_count() == 1
            assert buffer.get() is None


def test_process_pending_orders_empty_buffer():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "orders.mmap")

        with SharedMemoryRingBuffer(path, capacity=8) as buffer:
            book = CythonOrderBook()

            assert process_pending_orders(buffer, book) == 0
            assert book.get_trade_count() == 0

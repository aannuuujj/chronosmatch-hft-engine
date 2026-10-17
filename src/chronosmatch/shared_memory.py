"""Fixed-size shared-memory ring buffer for order messages."""

import mmap
import struct
from pathlib import Path

# order_id, side (0=BUY, 1=SELL), price, quantity, timestamp
_RECORD = struct.Struct("<QBqIq")
_HEADER = struct.Struct("<QQ")  # write position, read position


class SharedMemoryRingBuffer:
    """Single-process-safe ring buffer backed by a memory-mapped file.

    This initial version is intended for local testing.
    Cross-process synchronization will be added separately.
    """

    def __init__(self, path: str, capacity: int = 1024):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.path = Path(path)
        self.capacity = capacity
        self._size = _HEADER.size + capacity * _RECORD.size

        with self.path.open("wb") as file:
            file.truncate(self._size)

        self._file = self.path.open("r+b")
        self._map = mmap.mmap(self._file.fileno(), self._size)
        _HEADER.pack_into(self._map, 0, 0, 0)

    def put(
        self,
        order_id: int,
        side: int,
        price: int,
        quantity: int,
        timestamp: int,
    ) -> bool:
        write_pos, read_pos = _HEADER.unpack_from(self._map, 0)

        if write_pos - read_pos >= self.capacity:
            return False
        if side not in (0, 1):
            raise ValueError("side must be 0 (BUY) or 1 (SELL)")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        offset = _HEADER.size + (write_pos % self.capacity) * _RECORD.size
        _RECORD.pack_into(
            self._map, offset, order_id, side, price, quantity, timestamp
        )
        _HEADER.pack_into(self._map, 0, write_pos + 1, read_pos)
        return True

    def get(self) -> tuple[int, int, int, int, int] | None:
        write_pos, read_pos = _HEADER.unpack_from(self._map, 0)

        if read_pos >= write_pos:
            return None

        offset = _HEADER.size + (read_pos % self.capacity) * _RECORD.size
        record = _RECORD.unpack_from(self._map, offset)
        _HEADER.pack_into(self._map, 0, write_pos, read_pos + 1)
        return record

    def close(self) -> None:
        self._map.close()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

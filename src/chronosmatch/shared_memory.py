"""File-backed mmap ring buffer with inter-process locking."""

import mmap
import struct
from pathlib import Path

from filelock import FileLock

_RECORD = struct.Struct("<QBqIq")
_HEADER = struct.Struct("<QQ")


class SharedMemoryRingBuffer:
    """A bounded FIFO ring buffer protected by a process-level file lock."""

    def __init__(self, path: str, capacity: int = 1024):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.path = Path(path)
        self.capacity = capacity
        self._size = _HEADER.size + capacity * _RECORD.size
        self._lock = FileLock(str(self.path) + ".lock")

        with self._lock:
            if not self.path.exists() or self.path.stat().st_size != self._size:
                with self.path.open("wb") as file:
                    file.truncate(self._size)
                with self.path.open("r+b") as file:
                    with mmap.mmap(file.fileno(), self._size) as mapped:
                        _HEADER.pack_into(mapped, 0, 0, 0)

        self._file = self.path.open("r+b")
        self._map = mmap.mmap(self._file.fileno(), self._size)

    def put(
        self,
        order_id: int,
        side: int,
        price: int,
        quantity: int,
        timestamp: int,
    ) -> bool:
        if side not in (0, 1):
            raise ValueError("side must be 0 (BUY) or 1 (SELL)")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        with self._lock:
            write_pos, read_pos = _HEADER.unpack_from(self._map, 0)
            if write_pos - read_pos >= self.capacity:
                return False

            offset = _HEADER.size + (write_pos % self.capacity) * _RECORD.size
            _RECORD.pack_into(
                self._map, offset, order_id, side, price, quantity, timestamp
            )
            _HEADER.pack_into(self._map, 0, write_pos + 1, read_pos)
            return True

    def get(self) -> tuple[int, int, int, int, int] | None:
        with self._lock:
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

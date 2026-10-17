from chronosmatch.shared_memory import SharedMemoryRingBuffer


def test_put_and_get_order(tmp_path):
    path = str(tmp_path / "ring.bin")

    with SharedMemoryRingBuffer(path, capacity=4) as ring:
        order = (1, 0, 100, 5, 123)
        assert ring.put(*order) is True
        assert ring.get() == order
        assert ring.get() is None


def test_buffer_full(tmp_path):
    path = str(tmp_path / "ring.bin")

    with SharedMemoryRingBuffer(path, capacity=1) as ring:
        assert ring.put(1, 0, 100, 5, 123) is True
        assert ring.put(2, 1, 101, 3, 124) is False
        assert ring.get() == (1, 0, 100, 5, 123)


def test_ring_buffer_wraparound(tmp_path):
    path = str(tmp_path / "ring.bin")

    with SharedMemoryRingBuffer(path, capacity=2) as ring:
        assert ring.put(1, 0, 100, 1, 1)
        assert ring.put(2, 1, 101, 1, 2)
        assert ring.get() == (1, 0, 100, 1, 1)

        assert ring.put(3, 0, 102, 1, 3)
        assert ring.get() == (2, 1, 101, 1, 2)
        assert ring.get() == (3, 0, 102, 1, 3)
        assert ring.get() is None

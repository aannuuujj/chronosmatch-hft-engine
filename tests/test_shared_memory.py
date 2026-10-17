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

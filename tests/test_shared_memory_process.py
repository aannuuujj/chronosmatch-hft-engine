import multiprocessing
from chronosmatch.shared_memory import SharedMemoryRingBuffer


def writer(path, ready):
    with SharedMemoryRingBuffer(path, capacity=4) as ring:
        while not ring.put(101, 0, 100, 5, 123):
            pass
        ready.set()


def test_separate_process_can_read_written_order(tmp_path):
    path = str(tmp_path / "ring.bin")
    ready = multiprocessing.Event()

    # Initialize the buffer before starting the writer process.
    with SharedMemoryRingBuffer(path, capacity=4):
        pass

    process = multiprocessing.Process(target=writer, args=(path, ready))
    process.start()

    try:
        assert ready.wait(timeout=5), "Writer process did not finish"
        with SharedMemoryRingBuffer(path, capacity=4) as ring:
            assert ring.get() == (101, 0, 100, 5, 123)
    finally:
        process.join(timeout=5)
        if process.is_alive():
            process.terminate()
            process.join()
        assert process.exitcode == 0

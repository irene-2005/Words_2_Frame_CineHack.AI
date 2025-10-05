import threading
import queue
from typing import Callable, Any

_task_q = queue.Queue()


def worker_loop():
    while True:
        fn, args, kwargs = _task_q.get()
        try:
            fn(*args, **kwargs)
        except Exception:
            pass
        _task_q.task_done()


_thread = threading.Thread(target=worker_loop, daemon=True)
_thread.start()


def submit_job(fn: Callable[..., Any], *args, **kwargs):
    _task_q.put((fn, args, kwargs))

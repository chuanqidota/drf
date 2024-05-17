import multiprocessing


def worker_function(*args, **kwargs):
    print(f'Worker function with args {args} and kwargs {kwargs} is running.')


class MultiProcessQueue:
    """
        多进程队列
    """

    def __init__(self):
        self.queue = multiprocessing.Queue()

    def put(self, *args, **kwargs):
        self.queue.put((args, kwargs))

    def get(self):
        while True:
            args, kwargs = self.queue.get()
            worker_function(*args, **kwargs)

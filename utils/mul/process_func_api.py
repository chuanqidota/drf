import multiprocessing


def worker_function(*args, **kwargs):
    print(f'Worker function with args {args} and kwargs {kwargs} is running.')
    # 在这里执行你的任务


if __name__ == '__main__':
    args = (1, 2, 3)
    kwargs = {'kwargs1': "kwargs_value1", "kwargs2": "kwargs_value2"}
    p1 = multiprocessing.Process(target=worker_function, args=args, kwargs=kwargs)
    p2 = multiprocessing.Process(target=worker_function, args=args, kwargs=kwargs)
    p1.start()
    p2.start()
    p1.join()
    p2.join()

import multiprocessing


def worker_function(*args, **kwargs):
    print(f'Worker function with args {args} and kwargs {kwargs} is running.')


if __name__ == '__main__':
    args = (1, 2, 3)
    kwargs = {"key1": "value1", "key2": "value2"}
    # 创建进程池
    pool = multiprocessing.Pool(4)
    # 启动进程池中的进程
    pool.apply_async(worker_function, args=args, kwds=kwargs)

    # 最后关闭进程池
    pool.close()
    # 等待进程池中的进程结束
    pool.join()

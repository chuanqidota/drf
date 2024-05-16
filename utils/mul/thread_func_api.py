import threading
import time


def worker_function(*args, **kwargs):
    print(f'Worker function with args {args} and kwargs {kwargs} is running.')
    # 在这里执行你的任务


def worker_lock():
    """
        带锁
    :return:
    """
    with threading.Lock():
        print("lock")


if __name__ == '__main__':
    # 并发执行
    t1 = threading.Thread(target=worker_function, args=("arg1", "arg2"), kwargs={"kwargs1": "kwargs_value1"})
    t2 = threading.Thread(target=worker_function)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # 定时器执行
    timer1 = threading.Timer(5.0, worker_function, args=("arg1", "arg2"), kwargs={"kwargs1": "kwargs_value1"})
    timer2 = threading.Timer(7.0, worker_function, args=("arg1", "arg2"), kwargs={"kwargs2": "kwargs_value2"})
    timer1.start()
    timer2.start()
    print('Timers started, main program continues...')
    time.sleep(10)  # 暂停10秒，以便看到定时器执行的结果
    print('Main program finished.')

    t_lock = threading.Thread(target=worker_lock)
    t_lock.start()
    t_lock.join()

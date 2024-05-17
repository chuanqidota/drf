import concurrent.futures
import time
from concurrent.futures import ThreadPoolExecutor, wait


def worker_function(name):
    """模拟耗时操作的工作者函数"""
    print(f'Worker {name} started at {time.ctime()}')
    print(f'Worker {name} finished at {time.ctime()}')
    return name


if __name__ == '__main__':

    result = []
    # 创建一个线程池，最大工作线程数为4
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 提交任务到线程池，这里提交了两个任务
        futures = {executor.submit(worker_function, f'Thread-{i}') for i in range(1, 3)}  # 这里也可以数组
        # futures = [executor.submit(worker_function, f'Thread-{i}') for i in range(1, 3)]
        # 等待结束
        wait(futures)
        # 收集结果（如果任务有返回值的话），并打印完成状态
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()  # 获取任务的结果，如果有的话
                result.append(data)
                print(f'Task returned: {data}')
            except Exception as exc:
                print(f'Task generated an exception: {exc}')

    print('All threads completed.')
    print(result)

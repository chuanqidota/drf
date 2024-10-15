# -*- coding: utf-8 -*-
import time

import threadpool


# 具体的某个函数
def worker_function(_id, callback=None):
    result = _id  
    time.sleep(1)
    if callback is not None:
        callback(result)


# 回调函数，用于处理 worker_function 返回的结果
def handle_result(result):
    results.append(result)  # 将结果存储到列表中


if __name__ == '__main__':
    ids = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    results = []  # 用于保存所有结果

    var_list = []
    for _id in ids:
        # 添加回调函数 handle_result 到每个任务
        var_list.append(([_id], {'callback': handle_result}))

    pool = threadpool.ThreadPool(10)
    reqs = threadpool.makeRequests(worker_function, var_list)
    [pool.putRequest(req) for req in reqs]
    pool.wait()

    print("所有线程已完成")
    print(results)

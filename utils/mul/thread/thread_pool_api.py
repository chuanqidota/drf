import threadpool


def worker_function(_id):
    print(f'{_id}')


if __name__ == '__main__':

    var_list = []
    ids = [1, 2, 3]
    for id in ids:
        var_list.append(([id], None))

    pool = threadpool.ThreadPool(10)
    reqs = threadpool.makeRequests(worker_function, var_list)
    [pool.putRequest(req) for req in reqs]
    pool.wait()

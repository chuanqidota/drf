import multiprocessing


def producer(conn):
    """该函数将在生产者进程中执行"""
    for i in range(10):
        conn.send(i)
    conn.close()


def consumer(conn):
    """该函数将在消费者进程中执行"""
    while True:
        item = conn.recv()
        if item is None:
            break
        print(item)


if __name__ == '__main__':
    # 创建管道
    conn1, conn2 = multiprocessing.Pipe()
    # 创建生产者进程
    p1 = multiprocessing.Process(target=producer, args=(conn1,))
    # 创建消费者进程
    p2 = multiprocessing.Process(target=consumer, args=(conn2,))
    # 启动进程
    p1.start()
    p2.start()
    # 等待进程结束
    p1.join()
    # 发送结束信号
    conn1.send(None)
    p2.join()

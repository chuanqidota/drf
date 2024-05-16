import threading


class WorkerThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        # 调用父类的初始化方法
        super().__init__()

        # 存储参数
        self.args = args
        self.kwargs = kwargs

    def run(self):
        # 这里的run方法是线程启动后执行的
        self.work_function(*self.args, **self.kwargs)

    def work_function(self, *args, **kwargs):
        # 在这里执行你的任务，可以使用self.args和self.kwargs
        print(f"Working with: {args}, {kwargs}")


if __name__ == '__main__':
    # 创建工作线程，传递任意数量的位置参数和关键字参数
    args = (1, 2, 3)
    kwargs = {"key1": "value1", "key2": "value2"}
    t1 = WorkerThread(args, kwargs)
    t2 = WorkerThread(args, kwargs)

    # 启动线程
    t1.start()
    t2.start()

    # 等待所有线程结束
    t1.join()
    t2.join()


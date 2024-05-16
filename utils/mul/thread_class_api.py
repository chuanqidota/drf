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
    worker1 = WorkerThread('param1', 'param2', arg1='value1', arg2='value2')
    worker2 = WorkerThread('another_param1', arg1='value3')

    # 启动线程
    worker1.start()
    worker2.start()

    # 等待所有线程结束
    worker1.join()
    worker2.join()

    print('All threads finished.')

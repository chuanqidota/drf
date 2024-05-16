import multiprocessing


class WorkerProcessing(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        print(f"Worker received arguments: {self.args}, {self.kwargs}")
        # 在这里执行实际的工作逻辑
        self.work_function(*self.args, **self.kwargs)

    def work_function(self, *args, **kwargs):
        """示例工作逻辑，可以根据需要替换"""
        print(f"Working with: {args}, {kwargs}")


if __name__ == "__main__":
    # 创建参数
    args = (1, 2, 3)
    kwargs = {"key1": "value1", "key2": "value2"}

    p1 = WorkerProcessing(*args, **kwargs)
    p2 = WorkerProcessing(*args, **kwargs)
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("All workers have finished.")

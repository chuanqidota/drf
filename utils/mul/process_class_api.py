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
    position_args = (1, 2, 3)
    keyword_args = {"key1": "value1", "key2": "value2"}

    # 创建并启动进程
    processes = [WorkerProcessing(*position_args, **keyword_args) for _ in range(3)]
    for process in processes:
        process.start()

    # 等待所有进程结束
    for process in processes:
        process.join()

    print("All workers have finished.")

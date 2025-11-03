"""
@shared_task(bind=True) 是 Celery 中用于定义可共享任务并绑定任务实例的装饰器。它的核心作用是为任务提供对自身实例（self）的访问权限，从而允许任务在运行时动态操作任务状态、重试机制、获取上下文信息等。

适用场景：
需要任务重试：在任务内部调用 self.retry() 实现自定义重试逻辑。
访问任务上下文：获取任务 ID（self.request.id）、参数、重试次数等信息。
动态修改任务属性：例如根据运行环境调整重试超时时间。
任务状态跟踪：在长时间任务中更新进度或状态。
链式任务或复杂工作流：需要传递中间结果或控制后续任务行为。
"""


# 需要任务重试
# 场景：在任务中捕获异常并自定义重试逻辑（如 HTTP 请求失败时重试）。
from celery import shared_task
import requests

@shared_task(bind=True)  # 绑定任务实例
def fetch_url(self, url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 抛出 HTTP 错误
        return response.text
    except requests.RequestException as e:
        # 自定义重试：最多 3 次，每次间隔 10 秒
        self.retry(
            exc=e, 
            countdown=10, 
            max_retries=3
        )

# 访问任务上下文
# 场景：获取任务 ID、参数、重试次数等元数据

@shared_task(bind=True)
def log_task_details(self):
    # 访问任务上下文
    task_id = self.request.id           # 任务唯一 ID
    args = self.request.args             # 位置参数
    retries = self.request.retries       # 已重试次数
    hostname = self.request.hostname     # 执行任务的 Worker 名称

    print(f"Task {task_id} (retry {retries}) info: {args} {hostname}")



# 动态修改任务属性
# 场景：根据重试次数动态调整下一次重试的等待时间。
@shared_task(bind=True)
def unstable_task(self):
    try:
        # 模拟可能失败的操作（如依赖外部服务）
        if random.random() < 0.7:  # 70% 概率失败
            raise ValueError("Random failure!")
        return "Success"
    except Exception as e:
        # 动态调整重试间隔：重试次数越多，等待越久
        countdown = 2 ** self.request.retries  # 指数退避：2, 4, 8 秒...
        self.retry(exc=e, max_retries=5, countdown=countdown)


#任务状态跟踪
#场景：在长时间任务中更新进度（如文件处理或数据分析）
@shared_task(bind=True)
def process_large_file(self, file_path):
    total_lines = 1000  # 假设文件有 1000 行
    for i in range(total_lines):
        # 模拟处理单行数据
        time.sleep(0.1)
        
        # 更新任务进度（前端可通过 Backend 查询）
        progress = (i + 1) / total_lines * 100
        self.update_state(
            state="PROGRESS",
            meta={"progress": f"{progress:.1f}%", "current": i + 1}
        )
    
    return {"result": "File processed", "lines": total_lines}

# 链式任务或复杂工作流
# 场景：将任务 A 的结果传递给任务 B，并控制后续任务行为
from celery import chain

@shared_task(bind=True)
def task_a(self, x):
    result = x * 2
    # 触发任务 B，并传递结果
    task_b.apply_async(args=(result,))
    return result

@shared_task(bind=True)
def task_b(self, x):
    if x > 100:
        # 根据结果触发任务 C
        task_c.delay(x)
    return x + 10

@shared_task
def task_c(x):
    return x / 2

# 调用链式任务
chain(task_a.s(50), task_b.s(), task_c.s()).delay()

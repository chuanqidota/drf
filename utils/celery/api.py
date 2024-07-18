from celery import Celery

app = Celery('your_celery_app_name')

# 检查工作节点的在线状态
worker_status = app.control.inspect([worker]).ping()

# 返回工作节点的统计信息，如活动任务数、完成任务数等
worker_stats = app.control.inspect([worker]).stats()

# 返回活动任务的信息
active_tasks = app.control.inspect([worker]).active()

# 返回已注册任务的信息
registered_tasks = app.control.inspect([worker]).registered()

# 返回计划中的任务的信息
scheduled_tasks = app.control.inspect([worker]).scheduled()

# 返回已预订任务的信息
reserved_tasks = app.control.inspect([worker]).reserved()

# 返回已撤销任务的信息
revoked_tasks = app.control.inspect([worker]).revoked()

# 返回活动队列的信息
active_queues = app.control.inspect([worker]).active_queues()

# 查询worker的配置信息
worker_conf = app.control.inspect([worker]).conf()

# 返回工作节点的报告信息
worker_reports = app.control.inspect([worker]).report()

# 查询特定任务的信息
task_info = app.control.inspect([worker]).query_task(task_id)



from celery import Celery

app = Celery('your_celery_app_name')

result = app.AsyncResult(task_id)

# 获取任务状态
state = result.state

# 获取任务结果
result = result.result

# 返回一个布尔值，检查任务是否已经完成
is_ready = result.ready()

# 返回一个布尔值，检查任务是否成功完成
is_successful = result.successful()

# 返回一个布尔值，检查任务是否执行失败
is_failed = result.failed()

# 返回一个字符串，获取任务的错误追溯信息
traceback = result.traceback

# 返回一个AsyncResult对象，获取任务的父任务
parent_task = result.parent

# 返回一个列表，包含任务的子任务的AsyncResult对象，获取任务的子任务
child_tasks = result.children

# 返回一个字典，获取任务的其他信息
info = result.info

# 获取任务的结果，可以指定超时时间和是否向上传播异常
result = result.get(timeout=10, propagate=False)

# 忘记任务，将任务从结果存储中删除。一旦任务被遗忘，将无法查询其状态和结果
result.forget()
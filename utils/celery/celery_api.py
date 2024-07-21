from celery import Celery
from celery.schedules import crontab
"""
celery文档：http://www.celeryproject.org/

# 启动worker： celery -A celery_api worker --loglevel INFO -c 2 -Q duilie1 -D
# 启动beat:    celery -A celery_api beat -l info

参数
# 常用参数
-A 或 --app: 指定 Celery 应用程序的位置，通常是模块名称。
-c 或 --concurrency: 设置并行处理任务的进程数量，默认为系统可用的 CPU 数量。
-Q 或 --queues: 指定 worker 将从哪些队列读取任务。
-l 或 --loglevel: 设置日志级别，例如 INFO, DEBUG, WARNING 等。
-D 或 --detach: 后台运行 worker。
-f 或 --logfile: 日志文件的路径。
-P 或 --pool: 指定 worker 使用的池类型，如 prefork（默认）、eventlet、gevent 等。

-n 或 --hostname: 设置 worker 的主机名，用于区分同一台机器上的多个 worker 实例。
-E 或 --events: 开启事件监听，这将允许使用 Celery 的监控工具。
-B 或 --beat: 同时启动周期性任务调度器（beat）。
-O 或 --optimization: 设置优化选项，例如 fair 可以确保所有 worker 都能公平地获得任务。
-S 或 --scheduler: 当与 -B 一起使用时，指定调度器类。
-t 或 --time-limit: 设置任务的时间限制。
-s 或 --soft-time-limit: 设置任务的软时间限制。
-m 或 --maxtasksperchild: 设置每个子进程处理的最大任务数后，子进程将被重启。
-R 或 --autoscale: 设置自动扩展的最小和最大并发值
"""



app = Celery('tasks', broker="redis://localhost:6379/1", backend="redis://localhost:6379/2")





# 定时任务
app.conf.beat_schedule = {
    'send_cmd': {
        'task': '',  # 任务路径
        'schedule': crontab(minute="1", hour="1"),  # 定时周期
        'args': (),
        'kwargs': {},
    }
}


class CeleryHandler:
    """
        查看worker和task的状态
        以及查看task的执行结果
    """

    def __init__(self, app):
        self.app = app
        self.app.conf.update(
            CELERY_TASK_SERIALIZER='json',
            CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
            CELERY_RESULT_SERIALIZER='json',
            CELERY_TIMEZONE='Asia/Shanghai',
            CELERY_ENABLE_UTC=True,
        )

    def get_worker_status(self, worker=None):
        """
            查询所有worker的状态信息
        :return:
            {'celery@zqqzqqdeMacBook-Air.local': {'ok': 'pong'}}
        """
        if worker:
            return self.app.control.inspect([worker]).ping()
        return self.app.control.inspect().ping()

    def get_worker_config(self, worker):
        """
            获取节点的配置
        :param worker:
        :return:
            {
                'celery@zqqzqqdeMacBook-Air.local': {  # worker的标识符
                    'broker_url': 'redis://localhost:6379/1',  # 消息中间件（Broker）的URL
                    'result_backend': 'redis://localhost:6379/2',  # 结果后端的URL
                    'deprecated_settings': None,                # 已废弃的配置设置，如果存在的话
                    'include': ['api', 'celery.app.builtins']    # 包含的任务模块列表
                }
            }
        """
        if worker:
            return self.app.control.inspect([worker]).conf()
        return self.app.control.inspect([worker]).conf()

    def get_worker_stats(self, worker):
        """
        :param worker:
        :return:
            {
                'celery@zqqzqqdeMacBook-Air.local': {  # worker的标识符
                    'total': {},                       # 未使用的键，通常为空，用于统计任务总数
                    'pid': 4145,                       # worker的进程ID
                    'clock': '659',                    # worker本地的时间戳（单位：秒）
                    'uptime': 652,                     # worker的运行时间（单位：秒）
                    'pool': {                          # worker的进程池信息
                        'implementation': 'celery.concurrency.prefork:TaskPool',  # 进程池的实现类
                        'max-concurrency': 8,          # 最大并发数
                        'processes': [4150, 4151, ..., 4157],  # 进程池中的子进程ID列表
                        'max-tasks-per-child': 'N/A',  # 每个子进程最大执行任务数，'N/A'表示没有限制
                        'put-guarded-by-semaphore': False,  # 是否使用信号量保护任务放入队列的操作
                        'timeouts': [0, 0],            # 超时计数器，第一个元素为超时次数，第二个为超时总时间
                        'writes': {                    # 写入队列的信息
                            'total': 0,                # 总写入次数
                            'avg': '0.00',             # 平均写入时间
                            'all': '',                 # 所有写入时间的列表
                            'raw': '',                 # 原始写入时间的列表
                            'strategy': 'fair',        # 写入策略
                            'inqueues': {              # 输入队列信息
                                'total': 1,            # 总队列数
                                'active': 0            # 当前活动的队列数
                            }
                        }
                    },
                    'broker': {                        # 消息中间件（Broker）的信息
                        'hostname': 'localhost',       # Broker的主机名
                        'userid': None,                # Broker的用户ID
                        'virtual_host': '1',           # 虚拟主机名
                        'port': 6379,                  # Broker的端口号
                        'insist': False,               # 连接失败是否继续尝试
                        'ssl': False,                  # 是否使用SSL
                        'transport': 'redis',          # Broker的传输协议
                        'connect_timeout': 4,          # 连接超时时间
                        'transport_options': {},       # 传输层的额外选项
                        'login_method': None,          # 登录方法
                        'uri_prefix': None,            # URI前缀
                        'heartbeat': 120.0,            # 心跳间隔时间
                        'failover_strategy': 'round-robin',  # 故障转移策略
                        'alternates': []               # 备用Broker列表
                    },
                    'prefetch_count': 32,              # 预取任务的数量
                    'rusage': {                        # 资源使用情况
                        'utime': 1.010436,             # 用户态CPU时间
                        'stime': 0.34374099999999996,  # 系统态CPU时间
                        'maxrss': 68681728,            # 最大驻留集大小
                        'ixrss': 0,                    # 整页大小的共享内存大小
                        'idrss': 0,                    # 数据段大小
                        'isrss': 0,                    # 栈段大小
                        'minflt': 26946,               # 最小缺页中断数
                        'majflt': 803,                 # 重大缺页中断数
                        'nswap': 0,                    # 交换次数
                        'inblock': 0,                  # 输入块操作次数
                        'oublock': 0,                  # 输出块操作次数
                        'msgsnd': 1191,                # 发送消息次数
                        'msgrcv': 1522,                # 接收消息次数
                        'nsignals': 0,                 # 接收信号次数
                        'nvcsw': 1576,                 # 自愿上下文切换次数
                        'nivcsw': 4110                 # 非自愿上下文切换次数
                    }
                }
            }
        """
        if worker:
            return self.app.control.inspect([worker]).stats()
        return self.app.control.inspect().stats()

    def get_active_tasks(self, worker):
        """
            查看活动的任务
        :param worker:
        :return:
            {
                'celery@zqqzqqdeMacBook-Air.local': [  # worker的标识符
                    {
                        'id': 'd56e6ea0-809f-461b-9fd3-bff0dc68e034',  # 任务的唯一ID
                        'name': 'api.add',                           # 任务的名称
                        'args': [1, 2],                              # 任务的位置参数
                        'kwargs': {},                                # 任务的关键字参数
                        'type': 'api.add',                           # 任务的类型，通常与名称相同
                        'hostname': 'celery@zqqzqqdeMacBook-Air.local',  # 执行任务的worker的标识符
                        'time_start': 1721483000.2046626,           # 任务开始执行的时间戳
                        'acknowledged': True,                        # 任务是否已经被确认接收
                        'delivery_info': {                           # 交付给worker的信息
                            'exchange': '',                          # 任务消息的交换机
                            'routing_key': 'celery',                 # 任务消息的路由键
                            'priority': 0,                           # 任务的优先级
                            'redelivered': False                     # 任务是否是重新投递的
                        },
                        'worker_pid': 4775                           # 执行任务的worker的进程ID
                    }
                ]
            }
        """
        if worker:
            return self.app.control.inspect([worker]).active()
        return self.app.control.inspect().active()

    def get_registered_tasks(self, worker):
        """
            获取注册任务
        :param worker:
        :return:
            {
                'celery@zqqzqqdeMacBook-Air.local': [  # worker的标识符
                    'api.add'                           # 注册的任务名称
                ]
            }

        """
        if worker:
            return self.app.control.inspect([worker]).registered()
        return self.app.control.inspect().registered()

    def get_scheduled_tasks(self, worker):
        """

            获取定时任务信息
            或者直接从django_celery_beat_periodic_task表中获取
        :param worker:
        :return:
            {
                'celery@zqqzqqdeMacBook-Air.local': [  # worker的标识符
                    {
                        'request': {  # 任务请求的详细信息
                            'id': 'some-task-id',  # 任务的唯一ID
                            'name': 'tasks.periodic_task_name',  # 任务的名称
                            'args': [],  # 位置参数
                            'kwargs': {},  # 关键字参数
                            'eta': datetime.datetime(2023, 10, 1, 12, 0),  # 预定执行时间
                            'expires': None,  # 任务过期时间，如果任务在这个时间之后还未执行，则会被丢弃
                            'time_limit': None,  # 任务的最大执行时间
                            'soft_time_limit': None,  # 任务的软时间限制，在达到这个时间限制后，任务可以被优雅地终止
                            'retries': 0,  # 任务的重试次数
                            'retry_policy': None,  # 任务的重试策略
                            'callbacks': [],  # 任务完成后要调用的回调任务
                            'errbacks': [],  # 任务执行失败后要调用的回调任务
                            'chord': None,  # 如果任务是 Chord 模式的一部分，这里会有相关信息
                            'group_id': None,  # 如果任务是任务组的一部分，这里会有组ID
                            'taskset_id': None,  # 如果任务是 TaskSet 的一部分，这里会有 TaskSet 的ID
                            'parent_id': None,  # 如果任务是由另一个任务触发的，这里会有父任务的ID
                            'root_id': None,  # 如果任务是链式任务的一部分，这里会有根任务的ID
                            'replaced_by': None,  # 如果任务被另一个任务替换，这里会有新任务的ID
                            'shadow': None,  # 如果任务是 shadow 任务，这里会有相关信息
                            'utc': True,  # eta 和 expires 时间是否以UTC时间表示
                            'clock': 0,  # 任务的时钟
                            'eta_is_stored_as_utc': True,  # eta 是否以UTC时间存储
                            'expires_is_stored_as_utc': True,  # expires 是否以UTC时间存储
                            'type': 'tasks.periodic_task_name',  # 任务的类型
                            'headers': {}  # 任务的头部信息
                        },
                        'schedule': {  # 任务的调度信息
                            'relative': False,  # 调度是否是相对的
                            'remaining_runs': None,  # 任务剩余的运行次数
                            'next': datetime.datetime(2023, 10, 1, 12, 0),  # 下一次执行的时间
                            'last_run_at': None,  # 上一次执行的时间
                            'coalesce': True,  # 如果任务错过执行时间，是否合并多个执行
                            'nowfun': None,  # 获取当前时间的方法
                            'app': <celery.Celery object at 0x10f4b3a90>,  # Celery 应用实例
                            'options': {},  # 任务的额外选项
                            'run_every': crontab(minute=0, hour=12)  # 任务的运行频率，例如使用crontab表达式
                        }
                    }
                ]
            }
        """
        if worker:
            return self.app.control.inspect([worker]).scheduled()
        return self.app.control.inspect().scheduled()

    def get_task_result(self, task_id):
        """
            获取任务的执行结果
            # 但是可以通过django-celery-results 生成的表中获取.
        :param task_id:
        :return:
        """
        result = self.app.AsyncResult(task_id)
        return {
            # 当前任务的状态，如PENDING、STARTED、RETRY、FAILURE、SUCCESS
            'state': result.state,
            # 如果任务已完成并且成功，返回任务的结果；否则可能为None
            'result': result.result,
            # 任务是否已完成（无论成功还是失败）
            'ready': result.ready(),
            # 任务是否成功完成
            'successful': result.successful(),
            # 任务是否执行失败
            'failed': result.failed(),
            # 如果任务失败，返回失败时的堆栈跟踪信息；否则为None
            'traceback': result.traceback,
            # 如果任务是由另一个任务触发的，返回父任务的AsyncResult对象；否则为None
            'parent': result.parent,
            # 返回由当前任务触发的子任务的AsyncResult对象列表
            'children': result.children,
            # 如果任务在执行过程中更新了额外信息，返回这些信息；否则为None
            'info': result.info
        }

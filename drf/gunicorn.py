# coding: utf-8

from multiprocessing import cpu_count

# 服务地址
bind = "0.0.0.0:8080"

# 进程数
workers = cpu_count() * 2

# 每个进程创建线程池的容量
threads = cpu_count() * 5

# 工作进程类型，支持 sync（默认）, eventlet, gevent, or tornado, gthread, gaiohttp
# 配置了threads，如果值大于1，worker_class会默认设置成gthread
# worker_class

# 连接数，这是单个进程内的连接数
worker_connections = 600

# 进程的超时时间，如果某个进程的空闲时间超过这个时间，就会被kill并重新启动一个新进程
# 默认30
# timeout = 60

# 进程收到重启信号后，会留出一定的超时时间来完成当前任务，
# 如果超过这个时间没完成，则会强制重启
# 默认30
# graceful_timeout = 10

# 最大请求数，worker达到这个请求数，则会自动重启这个worker进程，可以有效限制内存泄漏
# 数量根据实际情况调整
max_requests = 20000

# 配合max_requests一起使用，对在0到max_requests_jitter之间随机选一个数加到max_requests上
# 避免出现worker同时重启的情况（如果使用了nginx，有两个以上节点，这个不配置，问题也不大）
max_requests_jitter = 500

loglevel = "info"
# 格式设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = "-"
errorlog = "-"
# accesslog = "/opt/panda/logs/panda_access.log"
# errorlog = "/opt/panda/logs/panda_error.log"

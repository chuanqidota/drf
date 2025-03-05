"""
flower文档：https://flower-docs-cn.readthedocs.io/zh/latest/

包含启动方式和接口
"""

"""
启动
celery -A celery_api flower --address=0.0.0.0 --port=5555 --broker=redis://127.0.0.1:6379/1
可以不指定项目直接启动
celery --broker=redis://127.0.0.1:6379/1 flower --address=0.0.0.0 --port=7788 --basic_auth=admin:admin --persistent=True --db=/opt/test

basic_auth 登陆的用户和密码
persistent 持久化存储
db 存储的地方
"""

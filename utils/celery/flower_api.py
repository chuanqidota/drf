"""
flower文档：https://flower-docs-cn.readthedocs.io/zh/latest/

包含启动方式和接口
"""

"""
启动
celery -A celery_api flower --address=0.0.0.0 --port=5555 --broker=redis://127.0.0.1:6379/1
"""

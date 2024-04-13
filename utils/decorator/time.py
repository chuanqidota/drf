import datetime
import time

from drf.utils import logger

import time
import datetime


def time_decorator(desc=None):
    """
    执行时间装饰器-查看耗时时间
    使用示例:
    @time_decorator('测试')
    def your_function():
        # your code here

    :param desc: 对函数的描述，如果未提供，则使用函数名作为描述
    :return: 装饰了的函数
    """

    def time_decorate(func):
        def time_decorate_in(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                func_result = func(*args, **kwargs)
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行出错: {e}")
                raise e
            finally:
                end_time = time.perf_counter()
                cos_time = round(float(end_time - start_time), 4)
                # 日志输出格式提取为常量
                log_format = (f"\n**********耗时检测*********\n"
                              f"函数名称:{func.__name__}\n"
                              f"函数描述:{desc if desc else func.__name__}\n"
                              f"开始时间:{datetime.datetime.now().strftime('%Y-%m-%d %X')}\n"
                              f"结束时间:{datetime.datetime.now().strftime('%Y-%m-%d %X')}\n"
                              f"函数耗时:{cos_time}\n"
                              f"****************************\n")
                logger.info(log_format)
            return func_result

        return time_decorate_in

    return time_decorate

import datetime
import time

from drf.utils import logger


def time_decorater(desc=None):
    """
        执行时间装饰器-查看耗时时间
        @time_decorater('测试')
        def test():
            time.sleep(1)

        :param desc: 描述
        :return:
            **********耗时检测*********
            函数名称:test
            函数描述:测试
            开始时间:2022-11-04 17:45:13
            结束时间:2022-11-04 17:45:14
            函数耗时:1.0116
            ****************************
    """

    def time_decorate(func):
        def time_decorate_in(*args, **kwargs):
            s, start_time = time.time(), datetime.datetime.now().strftime('%Y-%m-%d %X')
            func_result = func(*args, **kwargs)
            e, end_time = time.time(), datetime.datetime.now().strftime('%Y-%m-%d %X')
            cos_time = round(float(e - s), 4)
            logger.info(f"\n**********耗时检测*********\n"
                        f"函数名称:{func.__name__}\n"
                        f"函数描述:{desc if desc else func.__name__}\n"
                        f"开始时间:{start_time}\n"
                        f"结束时间:{end_time}\n"
                        f"函数耗时:{cos_time}\n"
                        f"****************************\n")
            return func_result

        return time_decorate_in

    return time_decorate

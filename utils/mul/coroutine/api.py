import asyncio
import time

"""
async 开头 只要调用就是coroutine
await 后面跟的是coroutine然后把它变成task,丢到event_loop中执行
asyncio.gather 让多个task一同执行，返回值按照顺序返回
"""


async def worker_function(delay, what):
    await asyncio.sleep(delay)
    return f"{what}-{delay}"


async def main():
    """
        调用方式
        asyncio.run(main())
    :return:
    """
    # 方式一：先创建tasks再丢到gather中
    # print(f"start-{time.strftime('%X')}")
    # tasks = [
    #     asyncio.create_task(worker_function(1, "a")),
    #     asyncio.create_task(worker_function(2, "b")),
    # ]
    # ret = await asyncio.gather(*(tasks))
    # print(f"end-{time.strftime('%X')}")
    # return ret

    # 推荐-方式二:直接把croutine丢到gather中
    print(f"start-{time.strftime('%X')}")
    ret = await asyncio.gather(
        worker_function(1, "a"),
        worker_function(2, "b")
    )
    print(f"end-{time.strftime('%X')}")
    return ret


def main2():
    """
        直接打印返回值
        一步一步的实现
    :return:
    """
    print(f"start-{time.strftime('%X')}")
    loop = asyncio.get_event_loop()
    task1 = loop.create_task(worker_function(1, "a"))
    task2 = loop.create_task(worker_function(2, "b"))
    task1.add_done_callback(lambda x: print(x.result()))  # 这里打印结果
    task2.add_done_callback(lambda x: print(x.result()))  # 事件回调
    loop.run_until_complete(asyncio.wait([task1, task2]))
    print(f"end-{time.strftime('%X')}")


if __name__ == '__main__':
    # 运行主协程
    _ret = asyncio.run(main())  # 会自动开启event_loop
    print(_ret)

    # 运行主协程
    # main2()

import schedule


def job():
    print("this is job")


def main():
    schedule.every(1).seconds.do(job)  # 每隔1秒执行一次job函数
    schedule.every(1).minutes.do(job)  # 每隔1分钟执行一次job函数
    schedule.every(1).hours.do(job)  # 每隔1小时执行一次job函数
    schedule.every(1).days.do(job)  # 每隔1天执行一次job函数
    schedule.every(1).weeks.do(job)  # 每隔1周执行一次job函数

    schedule.every(1).minute.at(":34").do(job)  # 每隔1分钟34秒执行job函数
    schedule.every(1).hour.at(":43").do(job)  # 每隔1小时43分执行job函数
    schedule.every().day.at("10:30").do(job)  # 每天10:30执行job函数

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    main()

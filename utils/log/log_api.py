import logging

def get_logger():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s %(levelname)s  %(message)s")

    stream_handler = logging.StreamHandler()  # 处理标准输出流
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename="XXXXXXXXXX.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # 处理文件
    logger.addHandler(file_handler)
    return logger
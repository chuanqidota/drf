import datetime
import json
import logging

from kafka import KafkaProducer


class KafkaLoggingHandler(logging.Handler):

    def __init__(self, topic, bootstrap_servers):
        super().__init__()
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'))
        self.topic = topic

    def emit(self, record):
        value = {
            "time": datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %X"),
            "msg": record.msg,
            "pathname": record.pathname,
            "levelname": record.levelname
        }
        self.producer.send(self.topic, value=value)

    def close(self):
        self.producer.flush()
        self.producer.close()
        super().close()

if __name__ == "__main__":
    topic,bootstrap_servers = "", ""
    kafka_handler = KafkaLoggingHandler(topic, bootstrap_servers)

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    kafka_handler.setFormatter(formatter)

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    logger.addHandler(kafka_handler)
    
    logger.info("测试")
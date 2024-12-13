import logging
from kafka import KafkaProducer

class KafkaLoggingHandler(logging.Handler):
    def __init__(self, topic, bootstrap_servers='localhost:9092'):
        super().__init__()
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self.topic = topic

    def emit(self, record):
        log_entry = self.format(record)
        self.producer.send(self.topic, value=log_entry.encode('utf-8'))

    def close(self):
        self.producer.flush()
        self.producer.close()
        super().close()

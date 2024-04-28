import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError


class KafkaManager:

    def __int__(self, bootstrap_servers, topic):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

    def producer(self, data):
        """
            生产者
        :param data: dict
        :return:
        """
        producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                 value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8'))
        try:
            producer.send(self.topic, data)
            producer.flush()
        except Exception as e:
            print(f"发送失败-{repr(e)}")
        finally:
            producer.close()

    def consumer(self, group_id=None, auto_offset_reset="latest"):
        """
            消费者
        :param group_id: 组id-不同组id可以消费重复消费相同的数据
        :param auto_offset_reset: 偏移量
        :return:
        """
        consumer = KafkaConsumer(self.topic,
                                 bootstrap_servers=self.bootstrap_servers,
                                 auto_offset_reset=auto_offset_reset,
                                 group_id=group_id,
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))
        for message in consumer:
            """
                功能函数写在这里
            """
            print(message.value)


if __name__ == '__main__':
    pass

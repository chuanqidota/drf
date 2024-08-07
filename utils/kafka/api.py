import json

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic


class KafkaManager:

    def __init__(self, bootstrap_servers, topic):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

    def create_topic(self, num_partitions=1, replication_factor=1):
        """
            创建主题
        :return:
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        new_topic = NewTopic(name=self.topic, num_partitions=num_partitions, replication_factor=replication_factor)
        admin_client.create_topics([new_topic])
        admin_client.close()

    def list_topics(self):
        """
            列举出topic
        :return:
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        topic_list = admin_client.list_topics()
        return topic_list

    def delete_topic(self):
        """
            删除topic
        :return:
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        admin_client.delete_topics([self.topic])
        admin_client.close()

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
    _kafka_hosts = "localhost:9200"
    _topic = "test-topic"
    KafkaManager(_kafka_hosts, _topic).create_topic()

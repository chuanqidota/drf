import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError


class KafkaManager:
    """
    使用 kafka-python 库实现的全面管理 Kafka 操作的类。

    属性:
        bootstrap_servers (str): 以逗号分隔的 host:port 对列表，用于与 Kafka 集群建立初始连接。
        producer_config (dict): 为 KafkaProducer 实例提供的额外配置选项。
        consumer_config (dict): 为 KafkaConsumer 实例提供的额外配置选项。
        topic (str): 执行操作的目标主题。
    """

    def __init__(self, bootstrap_servers, topic, producer_config=None, consumer_config=None):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

        # 默认的生产者配置
        default_producer_config = {
            'key_serializer': lambda x: x.encode('utf-8'),
            'value_serializer': lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
        }

        # 应用用户自定义的生产者配置
        if producer_config:
            default_producer_config.update(producer_config)
        self.producer_config = default_producer_config

        # 默认的消费者配置
        default_consumer_config = {
            'group_id': 'kafka-manager-consumer',
            'auto_offset_reset': 'latest',
            'enable_auto_commit': True,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8')),
        }

        # 应用用户自定义的消费者配置
        if consumer_config:
            default_consumer_config.update(consumer_config)
        self.consumer_config = default_consumer_config

        # 懒加载初始化生产者和消费者
        self._producer = None
        self._consumer = None

    @property
    def producer(self):
        """懒加载并返回 KafkaProducer 实例。"""
        if self._producer is None:
            self._producer = KafkaProducer(**self.producer_config, bootstrap_servers=self.bootstrap_servers)
        return self._producer

    @property
    def consumer(self):
        """懒加载并返回 KafkaConsumer 实例。"""
        if self._consumer is None:
            self._consumer = KafkaConsumer(**self.consumer_config, bootstrap_servers=self.bootstrap_servers,
                                           topics=[self.topic])
        return self._consumer

    def send_message(self, key, value, partition=None, timestamp_ms=None):
        """
        向配置的主题发送消息。

        参数:
            key (str): 消息键。
            value (dict): 作为 JSON 可序列化对象的消息负载。
            partition (int, optional): 消息应发送到的分区。如果不指定，由 Kafka 自动选择。
            timestamp_ms (int, optional): 与消息关联的时间戳（毫秒）。如果不指定，使用当前时间。

        """
        try:
            self.producer.send(self.topic, key=key, value=value, partition=partition, timestamp_ms=timestamp_ms)
            self.producer.flush()  # 确保消息发送后再返回
        except KafkaError as e:
            print(f"向 Kafka 发送消息时发生错误: {e}")

    def consume_messages(self, max_records=1, timeout_ms=5000):
        """
        从配置的主题消费消息。

        参数:
            max_records (int, optional): 单次调用中要获取的最大记录数。
            timeout_ms (int, optional): 等待获取记录的超时时间（毫秒）。

        返回:
            List[Tuple[str, dict]]: 一个包含已消费消息键和反序列化值的元组列表。
        """
        records = []
        try:
            records = self.consumer.poll(max_records=max_records, timeout_ms=timeout_ms)
        except KafkaTimeoutError:
            print("在指定的超时时间内未接收到任何消息。")

        # 从获取的记录中提取键和值
        consumed_messages = [(record.key.decode('utf-8'), record.value) for record in records.values()]
        return consumed_messages


if __name__ == '__main__':
    # 初始化 KafkaManager
    kafka_manager = KafkaManager(
        bootstrap_servers='localhost:9092',
        topic='my-topic',
    )

    # 发送消息
    kafka_manager.send_message(key='message_key', value={'data': '示例负载'})
    kafka_manager.producer.close()

    # 消费消息-可以修改配置
    messages = kafka_manager.consume_messages()
    for msg_key, msg_value in messages:
        print(f"键: {msg_key}, 值: {msg_value}")

    # 完成后关闭连接
    kafka_manager.consumer.close()

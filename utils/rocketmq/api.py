import json
import uuid

from rocketmq.client import Producer, Message, PushConsumer

"""
需要安装下面两个包
pip install rocketmq-client-python
pip install rocketmq
"""


class ProducerHandle(object):
    """
        生产者
        _topic = ""
        _cluster = ""
        _body = {}
        with ProducerHandle(_topic, _cluster, _body) as p:
            p.send_msg()
    """

    def __init__(self, topic, cluster, body, tags="change"):
        """
            初始化
        :param topic: 主题
        :param cluster: 集群
        :param body: 发送数据，不需要json.dumps()
        :param tags: 标签
        """
        self.topic = topic
        self.cluster = cluster
        self.producer = None
        self.msg = None
        self.body = body
        self.tags = tags
        self.key = uuid.uuid4().hex

    def __enter__(self):
        self.producer = Producer(self.topic)
        self.producer.set_namesrv_addr(self.cluster)
        self.producer.start()
        self.msg = Message(self.topic)
        self.msg.set_keys(self.key)
        self.msg.set_tags(self.tags)
        self.msg.set_body(json.dumps(self.body))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.producer.shutdown()

    def send_msg(self):
        """
             发送消息
        :return:
        """
        print(f"rocket-mq-发送消息-key-{self.key}-msg-{self.body}")
        ret = self.producer.send_sync(self.msg)
        print(f"rocket-mq-发送消息-结果-{ret.msg_id}")


class ConsumerHandle(object):
    """
        消费者
        _topic = ""
        _cluster = ""
        ConsumerHandle(_topic, _cluster).run()
    """

    def __init__(self, topic, cluster, group="pass_group"):
        self.topic = topic
        self.cluster = cluster
        self.group = group

    def run(self):
        consumer = PushConsumer(self.group)
        consumer.set_namesrv_addr(self.cluster)
        consumer.subscribe(self.topic, self.callback)
        consumer.start()  # 开启
        while True:
            pass

    @staticmethod
    def callback(msg):
        body = msg.body.decode("utf-8")
        body = json.loads(body)
        print(body)
        """do someting"""


if __name__ == '__main__':
    _topic = "****"
    _cluster = "rocketmq://****:9876;¥****:9876;****:9876"
    # 生产者
    """
    _body = {"data": "data"}
    with ProducerHandle(_topic, _cluster, _body) as p:
        p.send_msg()
    """
    # 消费者
    """
    ConsumerHandle(_topic, _cluster).run()
    """

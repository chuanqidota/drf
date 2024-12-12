from logging import Handler
from kafka import KafkaProducer


class KafkaLoggingHandler(Handler):

    def __init__(self, hosts_list, topic, key=None, partition=None, **kargs):
        """
        Kafka logging handler init function
        :param hosts_list: ‘host[:port]’ string (or list of ‘host[:port]’ strings)
        :param topic: kafka topic
        :param key: the key for kafka productor send msg
        :param partition: partition for kafka productor send msg
        :param kargs: Keyword Arguments from KafkaProducer, except bootstrap_servers
        """
        Handler.__init__(self)

        self.hosts_list = hosts_list
        self.topic = topic
        self.key = key
        self.partition = partition
        self.producter = KafkaProducer(bootstrap_servers=self.hosts_list, **kargs)

        # 获取 KafkaProducer 的后台线程对象_sender
        # 通过该线程对象判断 KafkaProducer 是否已经关闭
        # 问:为什么不通过KafkaProducer对象中的_closed属性判断
        # 答:因为调用close()方法时，到方法末尾才设置_closed标志，但是连接已经断开了，会导致异常的排除
        self._pro_sender = getattr(self.producter, "_sender")

    def emit(self, record):

        if record.name.startswith('kafka') and not getattr(self._pro_sender, "_running", False):
            # 如果producter已经关闭，且是kafka模块的日志
            # 则忽略kafka模块的输出

            # 问:为什么用self._pro_sender中的_closed属性判断
            # 答: self._pro_sender是 KafkaProducer 的后台线程对象，但是不能用is_alive()方法判断
            #    因为连接关闭后，还是会有日志输出，而_running属性是首先设置的
            return
        try:
            msg = self.format(record)
            self.producter.send(topic=self.topic, value=bytes(msg, encoding="utf8"),
                                partition=self.partition, key=self.key)
        except Exception:
            self.handleError(record)

    def close(self, timeout=None):
        Handler.close(self)
        try:
            self.producter.flush(timeout)
        except Exception:
            pass
        self.producter.close(timeout)

    def flush(self, timeout=None):
        self.producter.flush(timeout)
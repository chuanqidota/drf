import redis


class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        """
        初始化 Redis 连接
        :param host: Redis 服务器地址，默认为 'localhost'
        :param port: Redis 服务器端口，默认为 6379
        :param db: 使用的数据库编号，默认为 0
        :param password: Redis 密码，如果有的话
        """
        self.client = redis.Redis(host=host, port=port, db=db, password=password)

    def __enter__(self):
        """
        进入上下文管理器时，返回 Redis 连接对象
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        退出上下文管理器时，关闭 Redis 连接
        """
        self.close()

    def close(self):
        """
        关闭 Redis 连接
        """
        self.client.close()

    def set(self, key, value):
        """
        键值对操作>设置键值对
        :param key: 键
        :param value: 值
        :return: True/False
        """
        return self.client.set(key, value)

    # 过期时间。
    def setex(self, key, expire_time, value):
        """
        键值对操作>设置键值对，并设置过期时间
        :param key: 键
        :param value: 值
        :param expire_time: 过期时间（秒）
        :return True/False
        """
        return self.client.setex(key, expire_time, value)

    def get(self, key):
        """
        键值对操作>获取键对应的值
        :param key: 键
        :return: 值
        """
        return self.client.get(key)

    def delete(self, key):
        """
        键值对操作>删除键
        :param key: 键
        """
        self.client.delete(key)

    def exists(self, key):
        """
        键值对操作>检查键是否存在
        :param key: 键
        :return: 如果存在返回 1，否则返回 0
        """
        return self.client.exists(key)

    def hset(self, hash_key, field, value):
        """
        哈希表操作>在哈希表中设置字段和值
        :param hash_key: 哈希表的键
        :param field: 字段
        :param value: 值
        """
        self.client.hset(hash_key, field, value)

    def hget(self, hash_key, field):
        """
        哈希表操作>获取哈希表中的字段值
        :param hash_key: 哈希表的键
        :param field: 字段
        :return: 字段对应的值
        """
        return self.client.hget(hash_key, field)

    def hgetall(self, hash_key):
        """
        哈希表操作>获取哈希表中的所有字段和值
        :param hash_key: 哈希表的键
        :return: 字段和值的字典
        """
        return self.client.hgetall(hash_key)

    def lpush(self, list_key, *values):
        """
        列表操作>在列表头部插入值
        :param list_key: 列表的键
        :param values: 要插入的值，可以是多个
        """
        self.client.lpush(list_key, *values)

    def rpush(self, list_key, *values):
        """
        列表操作>在列表尾部插入值
        :param list_key: 列表的键
        :param values: 要插入的值，可以是多个
        """
        self.client.rpush(list_key, *values)

    def llen(self, list_key):
        """
        列表操作>获取列表的长度
        :param list_key: 列表的键
        :return: 列表的长度
        """
        return self.client.llen(list_key)

    def rpop(self, list_key):
        """
        列表操作>从列表尾部弹出一个值
        :param list_key: 列表的键
        :return: 弹出的值
        """
        return self.client.rpop(list_key)

    def saddr(self, set_key, *values):
        """
        集合操作>添加元素到集合
        :param set_key: 集合的键
        :param values: 要添加的元素
        """
        self.client.sadd(set_key, *values)

    def smembers(self, set_key):
        """
        集合操作>获取集合中的所有元素
        :param set_key: 集合的键
        :return: 集合中的所有元素
        """
        return self.client.smembers(set_key)

    def srem(self, set_key, *values):
        """
        集合操作>从集合中删除元素
        :param set_key: 集合的键
        :param values: 要删除的元素
        """
        self.client.srem(set_key, *values)

    def publish(self, channel, message):
        """
        发布消息到频道
        :param channel: 频道的键
        :param message: 要发布的消息
        """
        self.client.publish(channel, message)

    def subscribe(self, channel):
        """
        订阅频道
        :param channel: 频道的键
        """
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            print(message)
            # {'type': 'subscribe', 'pattern': None, 'channel': b'aaa', 'data': 1}
            if message['type'] == 'message':
                # yield message['data']
                print(message)


if __name__ == '__main__':
    with RedisManager() as client:
        # print(client.set("name1", "zhangsan"))
        # print(client.get("name"))
        # print(client.delete("name"))
        # print(client.exists("name"))
        # print(client.setex("name1", 30, "value"))
        # print(client.hset("hkey","field","value"))
        # print(client.hget("hkey","field"))
        # print(client.hgetall("hkey"))
        # print(client.lpush("list_key", "value1", "value2"))
        # print(client.llen("list_key"))
        # print(client.saddr("set_key", "value1", "value2", ""))
        # print(client.smembers("set_key"))

        print(client.publish("aaa", "bbb"))
        print(client.subscribe("aaa"))

import traceback

from etcd3.client import Etcd3Client

"""
出现这个错误的解决办法
Set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

pip uninstall protobuf        # 卸载原有protobuf库
pip install protobuf==3.20.0
"""


class EtcdManager:
    def __init__(self, host='localhost', port=2379, timeout=5, user=None, password=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.user = user
        self.password = password
        self.client = None

    def __enter__(self):
        self.get_client()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_client(self):
        """
            获取客户端
        :return:
        """
        self.client = Etcd3Client(host=self.host, port=self.port, timeout=self.timeout)

    def close(self):
        """
            关闭与etcd的连接
        :return:
        """
        self.client.close()

    def set_key_value(self, key, value, lease=None):
        """
            写入键值对
        :param key: 键名
        :param value: (str|bytes): 值，可以是字符串或字节串
        :param lease: (int|None): 附着的租约ID（可选）
        :return:
        """
        try:
            self.client.put(key, value, lease=lease)
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return False
        return True

    def get_key_value(self, key):
        """
            读取键值或字符串
        :param key: 键名
        :return: str|bytes: 值，根据原始写入类型返回字符串或字节串
        """
        response = self.client.get(key)
        return response[0].decode('utf-8')

    def delete_key(self, key):
        """
           删除键
        :param key: 键名
        :return: True/False
        """
        return self.client.delete(key)


if __name__ == '__main__':
    with  EtcdManager() as etcd_manager:
        etcd_manager.get_client()
        etcd_manager.set_key_value('test', 'test')
        # etcd_manager.get_key_value("test")
        # etcd_manager.delete_key("test")

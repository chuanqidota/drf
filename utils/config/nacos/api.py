from nacos import NacosClient

"""
pip install nacos-sdk-python
"""


class NacosHandler:
    def __init__(self, server_addresses, namespace_id, username, password):
        """
            初始化 Nacos 配置客户端。
        :param server_addresses: 服务地址
        :param namespace_id: namespace ID
        :param username: 用户名
        :param password: 密码
        """
        # 创建 Nacos 客户端实例
        self.client = NacosClient(
            server_addresses=server_addresses,
            namespace=namespace_id,
            username=username,
            password=password,

        )

    def get_config(self, data_id, group):
        """
        从 Nacos 获取指定 data_id 的配置信息。

        :param data_id: 要获取的配置的 dataId。
        :param group: 组。
        :return: 返回配置信息的字典，如果未找到则返回 None。
        """
        try:
            # 调用 Nacos 客户端的 get_config 方法获取配置信息
            config_info = self.client.get_config(data_id=data_id, group=group)
            return config_info
        except Exception as e:
            # 捕获并打印异常，返回 None 表示获取失败
            print(f"Error fetching configuration: {e}")
            return None

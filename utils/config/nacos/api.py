from nacos import NacosClient

"""
pip install nacos-sdk-python
"""
nacos_config = None  # 全局变量


class NacosHandler:
    def __init__(self, server_addresses, namespace_id, data_id, group, username=None, password=None):
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
        self.data_id = data_id
        self.group = group

    def get_config(self):
        """
        从 Nacos 获取指定 data_id 的配置信息。

        :return: 返回配置信息的字典，如果未找到则返回 None。
        """
        try:
            global nacos_config
            nacos_config = self.client.get_config(data_id=self.data_id, group=self.group)
        except Exception as e:
            # 捕获并打印异常，返回 None 表示获取失败
            print(f"Error fetching configuration: {e}")

    def watch_config(self):
        """
            监听配置
        :return:
        """
        self.client.add_config_watcher(self.data_id, self.group, self.__config_callback)

    @staticmethod
    def __config_callback(config):
        """
            配置回调
        :param config:
        :return:
        """
        global nacos_config
        nacos_config = config.get("content")

    def config_ini(self):
        """
            初始化
        :return:
        """
        self.get_config()
        self.watch_config()


if __name__ == '__main__':
    import time

    handle = NacosHandler("", "", "", "")
    handle.config_ini()
    while True:
        time.sleep(5)
        print(nacos_config)

import consul


class ConsulClient:
    """
        consul的相关操作
    """

    def __init__(self, host='localhost', port=8500, token=None):
        """
            初始化Consul客户端
        :param host: Consul服务的主机地址，默认为'localhost'。
        :param port: Consul服务的端口号，默认为8500。
        :param token: 访问Consul服务的令牌，默认为None。
        """
        self.client = consul.Consul(host=host, port=port, token=token)  # 创建Consul客户端实例

    def list_datacenters(self):
        """
            列出数据中心
        :return: 数据中心列表
        """
        return self.client.catalog.datacenters()

    def get_node_info(self, node):
        """
            获取节点信息
        :param node: 节点名称
        :return:
            ('338', {'Node': {'ID': 'db3565cc-6f2a-8ab0-e7e6-0b375e77442b', 'Node': 'zqqzqqdeMacBook-Air.local', 'Address': '127.0.0.1', 'Datacenter': 'dc1', 'TaggedAddresses': {'lan': '127.0.0.1', 'lan_ipv4': '127.0.0.1', 'wan': '127.0.0.1', 'wan_ipv4': '127.0.0.1'}, 'Meta': {'consul-network-segment': '', 'consul-version': '1.18.0'}, 'CreateIndex': 13, 'ModifyIndex': 14}, 'Services': {'My Service': {'ID': 'My Service', 'Service': 'my-service', 'Tags': ['tag1', 'tag2'], 'Address': '127.0.0.1', 'TaggedAddresses': {'lan_ipv4': {'Address': '127.0.0.1', 'Port': 8000}, 'wan_ipv4': {'Address': '127.0.0.1', 'Port': 8000}}, 'Meta': None, 'Port': 8000, 'Weights': {'Passing': 1, 'Warning': 1}, 'EnableTagOverride': False, 'Proxy': {'Mode': '', 'MeshGateway': {}, 'Expose': {}}, 'Connect': {}, 'PeerName': '', 'CreateIndex': 338, 'ModifyIndex': 338}, 'consul': {'ID': 'consul', 'Service': 'consul', 'Tags': [], 'Address': '', 'Meta': {'grpc_port': '8502', 'grpc_tls_port': '8503', 'non_voter': 'false', 'raft_version': '3', 'read_replica': 'false', 'serf_protocol_current': '2', 'serf_protocol_max': '5', 'serf_protocol_min': '1', 'version': '1.18.0'}, 'Port': 8300, 'Weights': {'Passing': 1, 'Warning': 1}, 'EnableTagOverride': False, 'Proxy': {'Mode': '', 'MeshGateway': {}, 'Expose': {}}, 'Connect': {}, 'PeerName': '', 'CreateIndex': 13, 'ModifyIndex': 13}}})
        """
        return self.client.catalog.node(node)

    def get_values_with_prefix(self, prefix):
        """
            查询指前缀的所有键值对
        :param prefix: 前缀
        :return:
        """
        _, data = self.client.kv.get(prefix, recurse=True)
        return [{"Key": entry['Key'], "Value": entry['Value'].decode('utf-8')}
                for entry in data]

    # KV operations
    def get_key_value(self, key):
        """
            获取键对应的值
        :param key:
        :return: 值
        """
        index, data = self.client.kv.get(key)
        # ('34', {'LockIndex': 0, 'Key': 'my/key', 'Flags': 0, 'Value': b'value', 'CreateIndex': 34, 'ModifyIndex': 34})
        if data:
            return data['Value'].decode('utf-8')
        else:
            return None

    def set_key_value(self, key, value):
        """
            设置键值
        :param key:
        :param value:
        :return: True/False
        """
        return self.client.kv.put(key, value)

    def delete_key(self, key, recurse=False):
        """
            删除指定的键。
        :param key:
        :param recurse: 如果为True，则递归删除与该键相关的所有项。默认为False
        :return: True/False
        """

        return self.client.kv.delete(key, recurse=recurse)

    def get_registered_services(self):
        """
            获取注册的服务
        :return:
            {
                'My Service': {
                    'ID': 'My Service',
                    'Service': 'my-service',
                    'Tags': ['tag1', 'tag2'],
                    'Meta': {},
                    'Port': 8000,
                    'Address': '127.0.0.1',
                    'TaggedAddresses': {
                        'lan_ipv4': {
                            'Address': '127.0.0.1',
                            'Port': 8000
                        },
                        'wan_ipv4': {
                            'Address': '127.0.0.1',
                            'Port': 8000
                        }
                    },
                    'Weights': {
                        'Passing': 1,
                        'Warning': 1
                    },
                    'EnableTagOverride': False,
                    'Datacenter': 'dc1'
                }
            }
        """
        return self.client.agent.services()

    def discover_service(self, service_name):
        """
            服务发现
        :param service_name: 服务名称 consul最外面的名称
        :return:
        """
        index, services = self.client.catalog.service(service_name)
        if services:
            return [{"address": service['ServiceAddress'], "port": service['ServicePort']} for service in services]
        else:
            return []

    def register_service(self, name, service_id, address, port, tags=None):
        """
            注册服务
        :param name: 服务名称 consul最外面的名称
        :param service_id: 服务id str consul内部的名称
        :param address: 地址
        :param port: 端口 int
        :param tags: 列表
        :return: True/False
        """
        definition = {
            "name": name,
            "service_id": service_id,
            "address": address,
            "port": port,
            "tags": tags
        }
        return self.client.agent.service.register(**definition)

    def deregister_service(self, service_id):
        """
            取消注册指定的服务
        :param service_id: 服务的id consul内部的页面的id
        :return: True/False
        """
        return self.client.agent.service.deregister(service_id)

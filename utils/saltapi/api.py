from urllib.parse import urljoin

import requests

"""
官方文档
https://docs.saltproject.io/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html


认证接口
/login: 用于获取认证令牌，通常需要提供用户名和密码。
执行命令
/run: 执行单个命令或模块功能在指定的目标上。
/cmd: 类似于/run，也用于执行命令，但提供了更详细的参数控制，如异步执行、批量操作等。
状态管理
/state: 应用或查询Salt状态，用于配置管理和部署。
轮询与事件
/events: 订阅Salt事件总线，监听Salt系统的各种事件。
/jobs: 查询作业状态和结果。
目标匹配
/minions: 列出所有可用的minions。
/tgt: 测试目标匹配表达式，检查哪些minions将被匹配。
配置管理
/config: 管理Salt配置，如获取或更新配置项。
键管理
/keys: 管理 minion 的公钥接受或拒绝。
轮询器（Schedules）管理
/schedule: 创建、修改或删除定时任务。
pillar数据管理
/pillar: 查询或更新Pillar数据。
** grains 数据管理**
/grains: 查询或更新Grains信息。
执行模块功能
/modules: 直接调用特定的Salt模块功能。
版本与系统信息
/version: 获取SaltStack的版本信息。
/sys: 系统信息和维护操作，如清理缓存等

"""


class SaltAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = self.get_token()

    def get_token(self):
        """
            通过用户名和密码获取令牌
        :return:
        """
        url = urljoin(self.base_url, "login")
        login_data = {
            'username': self.username,
            'password': self.password,
            'eauth': "pam"
        }
        response = requests.post(url, json=login_data)
        token = response.json()['return'][0]['token']
        return token

    def post(self, data, prefix='/'):
        """
            发起POST请求
        :param data:
        :param prefix:
        :return:
        """
        url = urljoin(self.base_url, prefix)
        headers = {'X-Auth-Token': self.token}
        res = requests.post(url, json=data, headers=headers, verify=False)
        return res.json()

    def all_key(self):
        """
        获取所有密钥的信息。

        :return: 返回一个包含 minions 和 minions_pre 的元组。
            minions: 已激活的矿工密钥列表。
            minions_pre: 未激活的矿工密钥列表。
        """
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        res = self.post(params)
        minions = res['return'][0]['data']['return']['minions']
        minions_pre = res['return'][0]['data']['return']['minions_pre']
        return minions, minions_pre

    def delete_key(self, node_name):
        """
        删除指定名称的节点密钥。

        :param node_name: 要删除的节点名称，用于匹配删除密钥。
        :return: 返回一个布尔值，表示删除操作是否成功。
        """

        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
        res = self.post(params)
        ret = res['return'][0]['data']['success']
        return ret

    def accept_key(self, node_name):
        """
        接受指定节点的key。

        :param node_name: 需要接受key的节点名称。
        :return: 返回一个布尔值，表示key接受是否成功。
        """

        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        res = self.post(params)
        ret = res['return'][0]['data']['success']
        return ret

    def salt_alive(self, tgt):
        """
        测试指定目标是否存活。

        :param tgt: 目标标识，可以是主机名、IP地址或标签等，用于指定需要测试的目标。
        :return: 返回一个布尔值，表示目标是否存活。如果目标存活，返回True；否则返回False。
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'test.ping'}
        res = self.post(params)
        ret = res['return'][0]
        return ret

    def run_command(self, tgt, fun, arg):
        """
        执行指定的命令

        :param tgt: 目标，指定命令执行的主机或主机集合
        :param fun: 函数名，指定要执行的命令
        :param arg: 参数，命令执行时需要的参数
        :return: 命令执行的结果
        """
        payload = {
            'client': 'local',
            'tgt': tgt,
            'fun': fun,
            'arg': arg
        }
        return self.post(payload)

    def salt_state(self, tgt, arg, expr_form):
        """
        执行Saltstack的州（state）管理操作。

        通过指定目标（tgt）、参数（arg）和表达式形式（expr_form），来调用Saltstack的local客户端执行指定的州管理命令。

        :param tgt: 目标标识，指定要应用州（state）的Saltstack Minion。可以是主机名、IP地址或标签等。
        :param arg: 传递给州（state）的参数。通常包括州ID或一组州ID。
        :param expr_form: 表达式形式，指定如何解释tgt参数。例如，'glob'、'pcre'、'list'等。
        :return: 返回执行州（state）管理操作的结果。结果是一个字典，包含执行详情和结果。

        例如，可能返回某个Minion应用指定州后的结果状态。
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': expr_form}
        res = self.post(params)
        ret = res['return'][0]
        return ret

    def async_exec(self, tgt, fun, arg):
        """
           异步执行指定的函数

       :param tgt: 目标，指定要执行函数的主机或主机集合
       :param fun: 要执行的函数名
       :param arg: 函数参数，可以是单个参数或参数列表
       :return: 返回一个作业ID（JID），该ID用于标识异步执行的作业
       """
        params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'list'}
        res = self.post(params)
        jid = res['return'][0]['jid']
        return jid

    def jobs_all_list(self):
        """
        获取所有任务列表的函数

        :return: 返回调用post方法后的结果
        """
        obj = {"client": "runner", "fun": "jobs.list_jobs"}
        res = self.post(obj)
        return res

    def get_jid_ret(self, jid):
        """
            通过jid获取执行结果
        :param jid: jobid
        :return: 结果
        """
        params = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': jid}
        res = self.post(params)
        ret = res['return'][0]
        return ret

    def running_jobs(self):
        """
            获取运行中的任务
        :return: 任务结果
        """
        params = {'client': 'runner', 'fun': 'jobs.active'}
        res = self.post(params)
        ret = res['return'][0]
        return ret


# 使用示例
if __name__ == "__main__":
    pass

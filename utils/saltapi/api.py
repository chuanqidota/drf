from urllib.parse import urljoin

import requests


class SaltAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = self.get_token(username, password)

    def get_token(self, username, password):
        url = urljoin(self.base_url, "login")
        login_data = {
            'username': username,
            'password': password,
            'eauth': "pam"
        }
        response = requests.post(url, json=login_data)
        token = response.json()['return'][0]['token']
        return token

    def post(self, data, prefix='/'):
        url = urljoin(self.base_url, prefix)
        headers = {'X-Auth-Token': self.token}
        res = requests.post(url, json=data, headers=headers, verify=False)
        return res.json()

    def list_all_key(self):
        """
            获取包括认证、未认证salt主机
        """

        params = {'client': 'wheel', 'fun': 'key.list_all'}
        res = self.post(params)
        minions = res['return'][0]['data']['return']['minions']
        minions_pre = res['return'][0]['data']['return']['minions_pre']
        return minions, minions_pre

    def delete_key(self, node_name):
        """
            删除key
        :param node_name:
        :return:
        """

        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
        res = self.post(params)
        ret = res['return'][0]['data']['success']
        return ret

    def accept_key(self, node_name):
        """
            接受key
        :param node_name:
        :return:
        """

        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        res = self.post(params)
        ret = res['return'][0]['data']['success']
        return ret

    def salt_alive(self, tgt):
        params = {'client': 'local', 'tgt': tgt, 'fun': 'test.ping'}
        res = self.post(params)
        ret = res['return'][0]
        return ret

    def run_command(self, tgt, fun, arg):
        payload = {
            'client': 'local',
            'tgt': tgt,
            'fun': fun,
            'arg': arg
        }
        return self.post(payload)

    def salt_state(self, tgt, arg, expr_form):
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': expr_form}
        res = self.post(params)
        ret = res['return'][0]
        return ret

    def async_exec(self, tgt, fun, arg):
        """
            远程异步执行模块，有参数
        :param tgt: minion list
        :param fun: 模块
        :param arg: 参数
        :return: jobid
        """
        params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'list'}
        res = self.post(params)
        jid = res['return'][0]['jid']
        return jid

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

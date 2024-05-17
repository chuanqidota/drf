import json

import requests

# from salt.utils.event import MasterEvent

"""
官方文档
https://docs.saltproject.io/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html

常用命令
salt-key -L 列出所有  
salt-key -a 允许一台 minion  
salt-key -A 允许所有  
salt-key -r 拒绝一台  
salt-key -R 拒绝所有  
salt-key -d 删除指定 minion  
salt-key -D 删除所有
salt-run manage.up 查看存活的key
salt-run manage.down 查看不存活的key

异步执行 跟上 --async

salt 'hostname' sys.list_functions cmd # 列出cmd的功能
salt "hostname" sys.doc cmd # 查询模块
salt "hostname" sys.doc cmd.run # 查询模块数名
salt 'hostname' sys.state_doc cmd # 查询state.sls文件写法

salt-run sys.doc jobs # 查看jobd的帮助文档

salt -L 'hostname,hostname2' cmd.run 'df -h' # 执行多台

salt-run jobs.lookup_jid 20240508035728435872 # 查询jid的结果


配置git
/etc/salt/master
fileserver_backend:
  - git

gitfs_remotes:
  - https://github.com/yourusername/your-repo.git

# 刷新文件
salt-run fileserver.update
"""


class SaltAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.login_url = f"{self.base_url}/login"  # 用于获取认证令牌
        self.token = self.get_token()  # token
        print(self.token)
        self.headers = {"X-Auth-Token": self.token, "Content-Type": "application/json"}
        self.keys_url = f"{self.base_url}/keys"  # 获取key
        self.events_url = f"{self.base_url}/events"  # 订阅Salt事件总线，监听Salt系统的各种事件 连接监听
        self.jobs_url = f"{self.base_url}/jobs"  # 查询作业状态和结果 GET
        self.run_url = f"{self.base_url}/run"  # 执行单个命令或模块功能在指定的目标上 GET
        self.minions_url = f"{self.base_url}/minions"  # 列出所有可用的minions GET

    def get_token(self):
        """
            通过用户名和密码获取令牌
        :return:
        """
        data = {
            'username': self.username,
            'password': self.password,
            'eauth': "pam"
        }
        response = requests.post(self.login_url, json=data)
        token = response.json()['return'][0]['token']
        return token

    def __get(self, url=None, params=None):
        """
            发起get请求
        :param url:
        :param params:
        :return:
        """
        if url and params:
            res = requests.get(url=url, params=params, headers=self.headers, verify=False).json()
        elif url and not params:
            res = requests.get(url=url, headers=self.headers, verify=False).json()
        else:
            res = None
        return res

    def __post(self, url=None, data=None):
        """
            发起post请求
        :param url:
        :param data:
        :return:
        """
        if url and data:
            res = requests.post(url, json=data, headers=self.headers, verify=False).json()
        elif url and not data:
            res = requests.post(url=url, headers=self.headers, verify=False).json()
        else:
            res = None
        return res

    def common(self, tgt, fun, arg, client='local', tgt_type="glob"):
        """
            通用执行命令

        :param tgt: 目标，指定命令执行的主机或主机集合
        :param fun: 函数名，指定要执行的命令
        :param arg: 参数，命令执行时需要的参数
        :param client:
            wheel等效于 通常管理主端资源，例如状态文件、支柱文件、Salt 配置文件
            local：等效于salt命令 这是最基础的客户端，用于在单个Minion上同步执行命令。它等待命令执行完成并返回结果。
            local_async：异步版本的local客户端，它不等待命令执行完成，而是立即返回一个job ID，可以在稍后查询结果。
            local_batch：这个客户端允许你以批处理的方式执行命令，例如按批次大小或百分比来分组Minion。
            local_subset：它允许你选择Minion子集来执行命令，而不是针对所有Minion。
            runner：等效于salt-run命令Runner客户端用于在Salt Master上执行特定的“runner”模块，这些模块通常是管理Master自身或辅助功能，如清理缓存、管理jobs等。
            runner_async：异步版本的runner客户端，与local_async类似，它不等待执行完成，而是返回job ID。
            ssh：SSH客户端允许通过SSH协议在远程主机上执行命令，即使这些主机不是Salt Minion。
            wheel：Wheel客户端用于与Salt的“wheel”模块交互，这些模块用于管理Salt Master的安全和配置，如添加、删除用户、管理pillar数据等。
            wheel_async：异步版本的wheel客户端，与前面的异步客户端一样，它不等待执行完成，而是返回job ID
        :param tgt_type:
                glob (默认)：
                使用 Bash 风格的通配符匹配 Minion ID。
                示例：'*' 匹配所有 Minions，'web*' 匹配以 "web" 开头的 Minions。
                pcre：
                使用 Perl 风格的正则表达式匹配 Minion ID。
                示例：'^web[0-9]+\.example\.com$' 匹配形如 "webX.example.com" 的 Minions。
                list：
                使用 Python 列表来指定确切的 Minion ID。
                示例：['minion1', 'minion2'] 直接指定要影响的 Minions。
                grain：
                根据 Minion 的 grains（元数据）来进行匹配。
                示例：'os:Ubuntu' 匹配 grains 中 os 字段值为 "Ubuntu" 的 Minions。
                pillar：
                基于 Minion 的 pillars（静态配置数据）进行匹配。
                示例：'roles:database' 匹配 pillar 中有 roles 字段且值为 "database" 的 Minions。
                ipcidr：
                使用 IP 网络地址和子网掩码来匹配 Minions。
                示例：'192.168.1.0/24' 匹配属于该子网的 Minions。
                range：
                使用 Salt 的 range matcher，基于 Minion ID 的序号。
                示例：'10-20' 匹配 ID 从 "minion10" 到 "minion20" 的 Minions。
                compound：
                使用复杂的组合匹配，可以结合多种匹配方式。
                示例：'G@os:Ubuntu and S@roles:database' 匹配既是 Ubuntu 操作系统的又具有数据库角色的 Minions
        :return: 命令执行的结果
        """
        body = {
            'client': client,
            'tgt': tgt,
            'fun': fun,
            'arg': arg,
            'tgt_type': tgt_type
        }
        res = self.__post(self.base_url, body)
        return res

    def async_common(self, tgt, fun, arg, client='local_async', tgt_type="glob"):
        """
           异步执行指定的函数

       :param tgt: 目标，指定要执行函数的主机或主机集合
       :param fun: 要执行的函数名
       :param arg: 函数参数，可以是单个参数或参数列表
       :param client:
       :param tgt_type:

       :return: 返回一个作业ID（JID），该ID用于标识异步执行的作业
       """
        body = {
            'client': client,
            'tgt': tgt,
            'fun': fun,
            'arg': arg,
            'tgt_type': tgt_type
        }
        res = self.__post(self.base_url, body)
        jid = res['return'][0]['jid']
        return jid

    def api_get_events(self, jid):
        """
            接口方式监听事件
            需要通过sls文件方式执行
        :param jid:
        :return:
        """
        minions = []
        completed_minions = set()
        while True:
            response = requests.get(url=self.events_url, headers=self.headers, stream=True)
            for line in response.iter_lines():
                # 忽略空行
                if line:
                    event = line.decode('utf-8')
                    event_data = json.loads(event[5:]) if event.startswith('data:') else None
                    if event_data and event_data.get('tag').startswith(f'salt/job/{jid}/new/'):
                        minions = event_data['data']['minions']
                    if event_data and \
                            event_data.get('tag').startswith(f'salt/job/{jid}/ret/') and \
                            event_data['data']['func'] == "state.sls":
                        minion_id = event_data['data']['id']
                        completed_minions.add(minion_id)
                        success = event_data['data'].get('success', False)
                        res = event_data['data']['return']
                        self.event_backup(jid, minion_id, success, res)
                        if len(completed_minions) == len(minions):
                            break
            self.event_end(jid)
            break

    def master_get_events(self, jid):
        """
            master节点事件监听
        :param jid:
        :return:
        """
        minions = []
        completed_minions = set()
        while True:
            event = MasterEvent("/var/run/salt/master")
            event_data = event.iter_events(full=True)
            for item in event_data:
                if item and \
                        item.get('tag').startswith(f'salt/job/{jid}/ret/') and \
                        event_data['data']['func'] == "state.sls":
                    minion_id = item['data']['id']
                    success = item['data'].get('success', False)
                    completed_minions.add(minion_id)
                    res = item['data']['return']
                    self.event_backup(jid, minion_id, success, res)
                    if len(completed_minions) == len(minions):
                        break
            self.event_end(jid)
            break

    @staticmethod
    def event_backup(jid, minion, success, res):
        """
            事件回调 继承后重写这个函数
        :param jid:
        :param minion:
        :param success:
        :param res:
        :return:
        """
        print(jid, minion, success, res)

    @staticmethod
    def event_end(jid):
        """
            时间结束回调
        :param jid:
        :return:
        """
        print(jid)

    def get_all_minions_info(self):
        """
            获取所有的minions信息
            机器的详细信息
        :return:
        """
        res = self.__get(self.minions_url)
        return res

    def get_minion_info(self, minion):
        """
            获取单个的minion信息
        :param minion: 支持正则 local*
        :return:
        """
        url = f'{self.minions_url}/{minion}'
        res = self.__get(url)
        return res

    def get_keys1(self):
        """
            获取所有keys
        :return:
            {
              "local": [
                "master.pem",
                "master.pub"
              ],
              "minions": [
                "localhost"
              ],
              "minions_denied": [],
              "minions_pre": [
                "10-10-0-193"
              ],
              "minions_rejected": []
            }
        """
        res = self.__get(self.keys_url)
        return res.get("return")

    def get_keys2(self):
        """
            获取所有密钥的信息。
        :return:
            {
              "local": [
                "master.pem",
                "master.pub"
              ],
              "minions": [
                "localhost"
              ],
              "minions_denied": [],
              "minions_pre": [
                "10-10-0-193"
              ],
              "minions_rejected": []
            }
        """
        body = {'client': 'wheel', 'fun': 'key.list_all'}
        res = self.__post(self.base_url, body)
        res = res['return'][0]['data']['return']
        return res

    def get_active_keys(self):
        """
            查看存活的minion
        """
        body = {'client': 'runner', 'fun': 'manage.up'}
        res = self.__post(self.base_url, body)
        res = res['return'][0]['data']['return']
        return res

    def get_deactive_keys(self):
        """
            查看不存活的minion
        """
        body = {'client': 'runner', 'fun': 'manage.down'}
        res = self.__post(self.base_url, body)
        res = res['return'][0]['data']['return']
        return res

    def accept_key(self, minion_id):
        """
            接受指定节点的key。
            操作范围 minions_pre
        :param minion_id: 需要接受key的节点名称。
        :return: 返回一个布尔值，表示key接受是否成功。
        """

        body = {'client': 'wheel', 'fun': 'key.accept', 'match': minion_id}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]['data']['success']
        return ret

    def reject_key(self, minion_id):
        """
            拒绝
            操作范围:minions_pre
        :param minion_id:
        :return:
        """
        body = {'client': 'wheel', 'fun': 'key.reject', 'match': minion_id}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]['data']['success']
        return ret

    def delete_key(self, minion_id):
        """
            删除指定名称的节点密钥。只能重启
            范围:所有的都可以删除
        :param minion_id: 要删除的节点名称，用于匹配删除密钥。
        :return: 返回一个布尔值，表示删除操作是否成功。
        """
        body = {'client': 'wheel', 'fun': 'key.delete', 'match': minion_id}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]['data']['success']
        return ret

    def ping_minion(self, minion, tgt_type="glob"):
        """
        测试指定目标是否存活。
        :param minion:
        :param tgt_type: 如果为list minion为列表 为批量
        :return: {'localhost': True}
        """
        body = {'client': 'local', 'tgt': minion, 'fun': 'test.ping', 'tgt_type': tgt_type}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def cmd_run(self, minion, cmd, tgt_type="glob"):
        """
            执行基础的bash命令
        :param minion:
        :param cmd:
        :param tgt_type: 如果为list minion为列表 为批量
        :return:
        """
        body = {'client': 'local', 'tgt': minion, 'fun': 'cmd.run', 'arg': cmd, 'tgt_type': tgt_type}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def state_sls(self, minion, arg, tgt_type="glob"):
        """
            执行state_sls
        :param minion: minion
        :param arg: sls文件path salt-master 配置文件
            file_roots:
               base:
                 - /srv/salt
                 # 这里在下面创建文件 比如 /srv/salt/init
                 # 创建 nginx.sls文件
                 # 然后命令就是 salt '*' state.sls init.nginx  这里的init.nginx就是路径
               dev:
                - /srv/salt-dev
                    :return: 返回执行州（state）管理操作的结果。结果是一个字典，包含执行详情和结果。
        :param tgt_type: tgt_type 如果为list minion为列表 为批量
        """
        body = {'client': 'local', 'tgt': minion, 'fun': 'state.sls', 'arg': arg, 'tgt_type': tgt_type}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def async_cmd_run(self, minion, cmd, tgt_type="glob"):
        """
            异步执行cmd命令
        :param minion:
        :param cmd:
        :param tgt_type: tgt_type 如果为list minion为列表 为批量
        :return:
        """
        body = {'client': 'local_async', 'tgt': minion, 'fun': "cmd.run", 'arg': cmd, 'tgt_type': tgt_type}
        res = self.__post(self.base_url, body)
        jid = res['return'][0]['jid']
        return jid

    def async_state_sls(self, minion, arg, tgt_type="glob"):
        """
            异步执行 sls文件
        :param minion:
        :param arg: 文件地址-相对地址
        :param tgt_type: tgt_type 如果为list minion为列表 为批量
        :return:
        """
        body = {'client': 'local_async', 'tgt': minion, 'fun': 'state.sls', 'arg': arg, 'tgt_type': tgt_type}
        res = self.__post(self.base_url, body)
        jid = res['return'][0]['jid']
        return jid

    def exec_pillar(self, minion, arg, tgt_type="glob", **kwargs):
        """
            执行pillar
        :param minion:
        :param arg:
        :param tgt_type:
        :param kwargs: pillar相关参数 字典
        :return:
        """
        body = {
            'client': 'local',
            'tgt': minion,
            'fun': 'state.sls',
            'arg': arg,
            'tgt_type': tgt_type,
            'kwarg': {'pillar': kwargs},
        }
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def async_exec_pillar(self, minion, arg, tgt_type="glob", **kwargs):
        """
            异步执行pillar
        :param minion:
        :param arg:
        :param tgt_type:
        :param kwargs:
        :return:
        """
        body = {
            'client': 'local_async',
            'tgt': minion,
            'fun': 'state.sls',
            'arg': arg,
            'tgt_type': tgt_type,
            'kwarg': {'pillar': kwargs},
        }
        res = self.__post(self.base_url, body)
        jid = res['return'][0]['jid']
        return jid

    def get_all_jobs1(self):
        """
            查询所有的jobs
        :return:
             [
                {
                    "20240508035728435872": {
                        "Function": "test.ping",
                        "Arguments": [],
                        "Target": "*",
                        "Target-type": "glob",
                        "User": "root",
                        "StartTime": "2024, May 08 03:57:28.435872"
                    },
                    "20240508072238680784": {
                        "Function": "cmd.run",
                        "Arguments": [
                            "cmd.cmd_run"
                        ],
                        "Target": "*",
                        "Target-type": "glob",
                        "User": "root",
                        "StartTime": "2024, May 08 07:22:38.680784"
                    }
                }
            ]
        """
        res = self.__get(self.jobs_url)
        return res.get("return", [])

    def get_all_jobs2(self):
        """
        获取所有任务列表的函数
        :return:
            [
                {
                    "20240508035728435872": {
                        "Function": "test.ping",
                        "Arguments": [],
                        "Target": "*",
                        "Target-type": "glob",
                        "User": "root",
                        "StartTime": "2024, May 08 03:57:28.435872"
                    },
                    "20240508072238680784": {
                        "Function": "cmd.run",
                        "Arguments": [
                            "cmd.cmd_run"
                        ],
                        "Target": "*",
                        "Target-type": "glob",
                        "User": "root",
                        "StartTime": "2024, May 08 07:22:38.680784"
                    }
                }
            ]
        """
        body = {"client": "runner", "fun": "jobs.list_jobs"}
        res = self.__post(self.base_url, body)
        return res.get("return", [])

    def get_job_res1(self, jid):
        """
            获取job详情
        :param jid:
        :return:
            res结果
            {
                "info": [
                    {
                        "jid": "20240508035728435872",
                        "Function": "test.ping",
                        "Arguments": [],
                        "Target": "*",
                        "Target-type": "glob",
                        "User": "root",
                        "Minions": [
                            "localhost"
                        ],
                        "StartTime": "2024, May 08 03:57:28.435872",
                        "Result": {
                            "localhost": {
                                "return": true,
                                "retcode": 0,
                                "success": true
                            }
                        }
                    }
                ],
                "return": [
                    {
                        "localhost": true
                    }
                ]
            }
        """
        url = f"{self.jobs_url}/{jid}"
        res = self.__get(url)
        return res["return"][0]

    def get_job_res2(self, jid):
        """
            通过jid获取执行结果
            只能获取minion存活的
            minion不存活/不存在都获取不到
        :param jid: jobid
        :return: 结果
            {'localhost': True}
        """
        body = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': jid}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def get_job_res3(self, jid):
        """
            通过jid获取执行结果
            只能获取minion存活的
            minion不存活/不存在都获取不到
        :param jid: jobid
        :return:
            {'jid': '20240516072151470283', 'Function': 'state.sls', 'Arguments': ['cmd.cmd_run'], 'Target': ['localhost', 'localhost12'], 'Target-type': 'list', 'User': 'saltapi', 'Minions': ['localhost'], 'StartTime': '2024, May 16 07:21:51.470283', 'Result': {'localhost': {'return': {'cmd_|-run_command_|-sleep 20 && echo "Hello, World!"_|-run': {'name': 'sleep 20 && echo "Hello, World!"', 'changes': {'pid': 2217, 'retcode': 0, 'stdout': 'Hello, World!', 'stderr': ''}, 'result': True, 'comment': 'Command "sleep 20 && echo "Hello, World!"" run', '__sls__': 'cmd.cmd_run', '__run_num__': 0, 'start_time': '15:21:52.128210', 'duration': 20030.115, '__id__': 'run_command'}}, 'retcode': 0, 'success': True, 'out': 'highstate'}}}
        """
        body = {'client': 'runner', 'fun': 'jobs.list_job', 'jid': jid}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def get_running_jobs(self):
        """
            获取运行中的任务
        :return:
            {'20240508075514416427': {'Function': 'state.sls', 'Arguments': ['cmd.cmd_run'], 'Target': 'localhost', 'Target-type': 'glob', 'User': 'saltapi', 'StartTime': '2024, May 08 07:55:14.416427', 'Running': [{'localhost': 1124}], 'Returned': []}}
        """
        body = {'client': 'runner', 'fun': 'jobs.active'}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def check_job_result(self, jid):
        """
            检查某个job是否已执行并成功退出
        :param jid:
            获取接受的key-(包含key存活和不存活都可以)
            不能获取不存在的
        :return True成功退出，False没有成功退出
        """
        body = {'client': 'runner', 'fun': 'jobs.exit_success', 'jid': jid}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret

    def update_git_file(self):
        """
            当git更新的时候-通过webhook让其执行接口，执行更新更新文件
        :return:
        """
        body = {'client': 'runner', 'fun': 'fileserver.update'}
        res = self.__post(self.base_url, body)
        ret = res['return'][0]
        return ret


# 使用示例
if __name__ == "__main__":
    """
        /srv/salt/cmd/cmd_run.sls
        run_command:
          cmd.run:
            - name: sleep 5 && echo "Hello, World!"

        /srv/salt/cmd/pillar_demo.sls
        {% set my_param = salt['pillar.get']('version', 'default_value') %}
        pillar_test:
          cmd.run:
            - name: echo {{ my_param }}
    """

    _base_url = "http://10.10.0.193:8090"
    _username = "saltapi"
    _password = "python"
    s = SaltAPI(_base_url, _username, _password)
    _minion_id = ["localhost", "localhost1"]
    # print(s.get_keys2())
    # # print(s.delete_key(_minion_id))
    # print(s.accept_key(_minion_id))
    # print(s.reject_key(_minion_id))
    # print(s.get_keys2())
    # print(s.reject_key(_minion_id))
    # print(s.ping_minion(_minion_id, "list"))
    # _jid = s.async_state_sls(_minion_id, 'cmd.cmd_run', "list")
    # print(_jid)
    # s.api_get_events(_jid, [_minion_id])
    # print(s.check_job_result(20240517021144534608))
    # print(s.get_running_jobs())

    # print(s.exec_pillar("localhost", "cmd.pillar_demo", **{"version": "aaaa"}))

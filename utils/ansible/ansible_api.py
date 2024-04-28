"""
项目依赖
ansible==9.5.1
ansible-base==2.10.17
"""
import json

from ansible import context
from ansible.module_utils.common.collections import ImmutableDict

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.executor.playbook_executor import PlaybookExecutor

import ansible.constants as C

# 注意： 该配置是为了避免没有第一次公钥访问写入 know_hosts 文件问题，
C.HOST_KEY_CHECKING = False


class ResultCallback(CallbackBase):
    """
        回调函数
        ad-hoc和playbook执行结果回调
    """

    def on_any(self, *args, **kwargs):
        """
            任何情况都会回调
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def runner_on_failed(self, host, res, ignore_errors=False):
        """
            当Ansible在目标主机上执行任务失败时触发
        :param host: 表示失败的主机名
        :param res: 包含失败任务的详细结果
        :param ignore_errors: 指示是否忽略此错误并继续执行
        :return:
        """
        print(json.dumps({host: res}, indent=2))

    def runner_on_ok(self, host, res):
        """
            在目标主机上成功执行任务时触发
        :param host:表示成功执行任务的主机名
        :param res:包含任务成功的详细结果
        :return:
        """
        print(json.dumps({host: res}, indent=2))

    def runner_on_unreachable(self, host, res):
        """
            无法连接到目标主机或主机被视为不可达时触发
        :param host:表示不可达的主机名
        :param res:包含有关不可达状态的详细信息
        :return:
        """
        print(json.dumps({host: res}, indent=2))

    def runner_on_no_hosts(self):
        print("runner_on_no_hosts")

    def runner_on_async_poll(self, host, res, jid, clock):
        """
            在目标主机上执行异步任务时触发
        :param host:表示正在执行异步任务的主机名
        :param res:包含异步任务状态的详细信息
        :param jid:异步任务ID
        :param clock:表示任务执行的时间
        :return:
        """
        print(json.dumps({"host": host, "res": res, "jid": jid, "clock": clock}, indent=2))

    def runner_on_async_ok(self, host, res, jid):
        """
            在目标主机上执行异步任务成功时触发
        :param host:表示执行异步任务的主机名
        :param res:包含异步任务成功状态的详细信息
        :param jid:异步任务ID
        :return:
        """
        print(json.dumps({"host": host, "res": res, "jid": jid}, indent=2))

    def runner_on_async_failed(self, host, res, jid):
        """
            在目标主机上执行异步任务失败时触发
        :param host:表示执行异步任务的主机名
        :param res:包含异步任务失败状态的详细信息
        :param jid:异步任务ID
        :return:
        """
        print(json.dumps({"host": host, "res": res, "jid": jid}, indent=2))

    def playbook_on_start(self):
        """
            当开始执行Ansible playbook时触发
        :return:
        """
        print("playbook_on_start")

    def playbook_on_stats(self, stats):
        """
            执行完毕并汇总执行统计信息时触发
        :param stats: 参数stats包含整个playbook执行的统计结果，如成功、失败、跳过的主机数等
        :return:
        """
        print({
            "changed": stats.changed,
            "custom": stats.custom,
            "failures": stats.failures,
            "ok": stats.ok,
            "processed": stats.processed,
            "skipped": stats.skipped,
            "dark": stats.dark,
            "rescued": stats.rescued
        })


class AnsibleManager(object):
    # 设置Ansible环境
    context.CLIARGS = ImmutableDict(
        connection='paramiko',  # 指定Ansible与目标主机之间的连接类型 paramiko/ssh
        remote_user=None,  # 指定执行任务时在远程主机上使用的用户名
        listtags=None, listhosts=None, listtasks=None,  # 是否列出已定义的标签（listtags）、主机列表（listhosts）或任务列表（listtasks
        module_path=None,  # 指明Ansible查找自定义模块的路径
        verbosity=5,  # 控制Ansible输出详细程度（日志级别）0-5
        ask_sudo_pass=False,  # 决定Ansible是否在执行需要提升权限的任务时提示用户输入sudo密码
        private_key_file=None,  # 指定用于SSH连接的私钥文件路径
        become=False,  # 设置为True表示需要提升权限执行任务 / 这里设置为True 可能会失败
        become_method=None,  # 值为None意味着使用默认的提权方法（通常为sud或sudo，取决于系统配置或Ansible配置文件
        become_user="root",  # 指定提升权限后的用户为'root'
        forks=10,  # 指定Ansible同时并发连接的最大数量
        check=False,  # 设置为False表示不启用“Dry Run”模式。如果设为True，Ansible将仅检查 playbook 的语法和任务
        diff=False,  # 当设为False时，Ansible不会显示任务执行前后配置文件或模板的差异
        syntax=None,  # 设置为True表示仅检查playbook的语法，不执行任务
        start_at_task=None,  # 如果提供了某个任务名称，Ansible将从playbook中的该任务开始执行，跳过之前的所有任务。值为None意味着从playbook的起始处按顺序执行所有任务
    )

    # 一般使用ansible的时候都会通过免密的方式，所以这里直接初始化passwords变为空
    def __init__(self, sources=None):
        C.DEFAULT_STDOUT_CALLBACK = ResultCallback()  # 设置回调
        self.passwords = dict()  # 如果是密码为dict(become_pass='0815')

        # 加载库存
        self.loader = DataLoader()  # 用来加载解析yaml文件或JSON内容,并且支持vault的解密
        self.inventory = InventoryManager(loader=self.loader, sources=sources)

        # 初始化变量管理器
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)  # 管理变量的类,包括主机,组,扩展等变量

    def run_adhoc(self, name, hosts, tasks, gather_facts="no"):
        """
            执行ad-hoc 任务
        :param name: 任务名称 字符串
        :param hosts: 主机列表
        :param tasks: [{"action":{"module":"","args":""}}]
        :param gather_facts: 采集主机信息 yes/no
        :return:
        """
        play_source = dict(
            name=name,
            hosts=hosts,
            gather_facts=gather_facts,  # 是否收集facts信息
            tasks=tasks
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                # stdout_callback=self.result_callback, # 这里改为全局回调
                # run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
                # run_tree=False,
            )
            tqm.run(play)  # 执行结果都在回调中
        finally:
            tqm.cleanup()
            self.loader.cleanup_all_tmp_files()  # 清理临时文件

    def run_playbook(self, playbook):
        """
            执行ansible-playbook
            剧本中最好配置gather_facts: false 不然每次都要采集主机信息
        :param playbook: 剧本路径列表
        :return:
        """
        playbook = PlaybookExecutor(
            playbooks=playbook,
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords,
        )
        playbook.run()


if __name__ == '__main__':
    """
    ad-hoc和playbook的结果都会在回调函数中体现
    可以重写回调函数来处理结果
    """

    """
    host.ini 文件内容
    [local]
    localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python3
    
    ping_book.yaml 文件内容
    ---
    - name: test-playbook-name
      hosts: localhost
      gather_facts: false
      tasks:
        - name: test-playbook-task
          ansible.builtin.ping:
    """
    _sources = ['/Users/zqqzqq/ansible/hosts.ini']
    a = AnsibleManager(_sources)
    host_list = ['localhost']
    task_list = [
        # dict(action=dict(module='command', args="df -h")),
        dict(action=dict(module='command', args="pwd"))
    ]
    # a.run_adhoc(name="任务名", hosts=host_list, tasks=task_list)

    _playbook = ["/Users/zqqzqq/ansible/playbook/ping_book.yml", "/Users/zqqzqq/ansible/playbook/ping_book.yml"]
    a.run_playbook(playbook=_playbook)

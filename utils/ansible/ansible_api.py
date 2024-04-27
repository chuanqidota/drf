import json
import shutil

from ansible import context
from ansible.module_utils.common.collections import ImmutableDict

"""
ansible==9.5.1
ansible-base==2.10.17
"""

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

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_playbook_on_play_start(self, play):
        print("playbook_on_play_start: %s" % play.name)

    def v2_runner_on_failed(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


class AnsibleApi:
    context.CLIARGS = ImmutableDict(
        connection='ssh', remote_user=None, listtags=None, listhosts=None, listtasks=None,
        module_path=None, verbosity=5, ask_sudo_pass=False, private_key_file=None,
        become=True, become_method=None, become_user='root',
        forks=10, check=False, diff=False, syntax=None, start_at_task=None,
    )

    # 一般使用ansible的时候都会通过免密的方式，所以这里直接初始化passwords变为空
    def __init__(self, sources=None):
        # self.name = name
        # self.host_list = host_list
        # self.task_list = task_list

        self.result_callback = ResultCallback()
        self.passwords = dict(become_pass='0815')
        # self.passwords = dict()

        self.loader = DataLoader()  # 用来加载解析yaml文件或JSON内容,并且支持vault的解密
        self.inventory = InventoryManager(loader=self.loader, sources=sources)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)  # 管理变量的类,包括主机,组,扩展等变量

    def run_adhoc(self, name, hosts, tasks):
        play_source = dict(
            name=name,
            hosts=hosts,
            gather_facts='no',
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
                stdout_callback=self.result_callback,
                # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
                # run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
                # run_tree=False,
            )
            result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
            return result
        finally:
            if tqm is not None:
                tqm.cleanup()
            self.loader.cleanup_all_tmp_files()

    def run_playhook(self, playbook):
        # self.variable_manager.extra_vars = {
        #     'customer': 'test',
        #     'disabled': 'yes'
        # }
        playbook = PlaybookExecutor(
            playbooks=playbook,
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords,
        )
        result = playbook.run()
        return result


if __name__ == '__main__':
    _sources = ['/Users/zqqzqq/ansible/hosts']
    a = AnsibleApi(_sources)

    host_list = ['localhost']
    task_list = [
        dict(action=dict(module='command', args="ls -l"))
        # dict(action=dict(module='command', args="pwd"))
    ]
    print(a.run_adhoc(name="checkConnection", hosts=host_list, tasks=task_list))
    # print(a.run_playhook(playbook=["/Users/zqqzqq/ansible/playbook/ping_book.yml"]))

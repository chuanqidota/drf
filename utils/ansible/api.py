import json
import shutil

from ansible import context
from ansible.module_utils.common.collections import ImmutableDict

# 注意: 使用namedtuple实现Options的方式，官网已经不推荐使用
#       网上很多例子都是按照Options的方式，会有报错如下：
# error_msg: "msg": "the connection plugin '<class 'ansible.utils.sentinel.Sentinel'>' was not found",
# 网上提供解决方案： https://blog.csdn.net/FMT21/article/details/103468284
# 但是目前验证报错，options 最终的tuple类型，在初始化的时候用到了 vars 系统函数，但是该函数报错
# TypeError: vars() argument must have __dict__ attribute
# from collections import namedtuple
# Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
# options = Options(connection='ssh', module_path=['/to/mymodules'], forks=10, become=None, become_method=None, become_user=None, check=False, diff=False)

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.executor.playbook_executor import PlaybookExecutor

import ansible.constants as C

# 注意： 该配置是为了避免没有第一次公钥访问写入 know_hosts 文件问题，
# 关于如何避免该问题，详见
C.HOST_KEY_CHECKING = False


class ResultCallback(CallbackBase):

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


class AnsibleApi:
    """
    Description:
    """

    context.CLIARGS = ImmutableDict(
        connection='ssh', remote_user=None, listtags=None, listhosts=None, listtasks=None,
        module_path=None, verbosity=5, ask_sudo_pass=False, private_key_file=None,
        become=True, become_method='sudo', become_user='root',
        forks=10, check=False, diff=False, syntax=None, start_at_task=None,
    )

    """

    Options = namedtuple('Options', ['connection', 'remote_user', 'listtags', 'listhosts', 'listtasks',
        'module_path', 'verbosity', 'ask_sudo_pass', 'private_key_file',
        'become', 'become_method', 'become_user',
        'forks', 'check', 'diff', 'syntax', 'start_at_task'])
    options = Options(
        connection='ssh', remote_user=None, listtags=None, listhosts=None, listtasks=None,
        module_path=None, verbosity=5, ask_sudo_pass=False, private_key_file=None,
        # become=None, become_method=None, become_user=None,
        become=True, become_method='sudo', become_user='root',
        forks=10, check=False, diff=False, syntax=None,start_at_task=None,
    )
    # 报错: TypeError: vars() argument must have __dict__ attribute
    context._init_global_context(options)
    """

    # 一般使用ansible的时候都会通过免密的方式，所以这里直接初始化passwords变为空
    def __init__(self):
        # self.name = name
        # self.host_list = host_list
        # self.task_list = task_list
        self.loader = DataLoader()
        self.result_callback = ResultCallback()
        # self.passwords = dict(vault_pass=passwords)
        self.passwords = dict()
        self.inventory = InventoryManager(loader=self.loader, sources=['/Users/zqqzqq/ansible/hosts'])
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

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
                run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
                run_tree=False,
            )
            result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
            print(result)
        finally:
            # we always need to cleanup child procs and the structres we use to communicate with them
            if tqm is not None:
                tqm.cleanup()

            # Remove ansible tmpdir
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

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
    a = AnsibleApi()
    host_list = ['localhost']
    task_list = [
        dict(action=dict(module='shell', args="ls -l"))
    ]
    a.run_adhoc(name="checkConnection", hosts=host_list, tasks=task_list)
    # print(a.run_playhook(playbook=["/Users/zqqzqq/ansible/playbook/ping_book.yml"]))

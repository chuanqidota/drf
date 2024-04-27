"""
ansible-runner==2.3.6

run参数含义
private_data_dir	str	包含 Runner 元数据所需的所有文件的目录，用于调用 Runner 模块。输出结果也将存储在此处以便后续消费。
playbook	str或list	要在 Ansible 执行时调用的 playbook（可以是 play 或 play 列表，或者相对于 private_data_dir/project 的路径）。
rotate_artifacts	int	最多保留 n 个工件目录，禁用则为 0（默认值）。用来控制运行结果的保留个数，0为全保存，用来清理产生的结果，非常方便
envvars	dict	Ansible 执行时要使用的环境变量。还将从 private_data_dir 中的 env/envvars 中读取环境变量。
extravars	dict	在 Ansible 运行时通过 -e 传递的额外变量。还将从 private_data_dir 中的 env/extravars 中读取额外变量。
ssh_key	str	作为 ansible-playbook 运行的一部分传递给 ssh-agent 的 SSH 私钥。
artifact_dir	str	要在其中存储工件（artifact）的目录的路径，默认为 private_data_dir 中的 'artifacts'。
cmdline	str	从 private_data_dir 中的 env/cmdline 中读取的 Ansible 命令行选项。
limit	str	与 ansible 的 --limit 参数匹配以进一步限制要使用的清单。
forks	int	控制 Ansible 并行并发性。
verbosity	int	控制 ansible-playbook 的输出详细程度。
quiet	bool	禁用所有输出。
event_handler	Callable	可选回调，在 Runner 本身接收到任何事件时被调用，返回 True 以保留事件。
cancel_callback	Callable	可选回调，可以通知 Runner 取消（返回 True）或不取消（返回 False）。
finished_callback	Callable	可选回调，在关闭进程并完成清理后被调用。
status_handler	Callable	可选回调，每当状态发生变化（例如...启动、运行、失败、成功、超时）时被调用。
artifacts_handler	Callable	可选回调，在运行结束时处理来自运行的工件。
json_mode	bool	在控制台和 stdout 文件中以 JSON 格式存储事件数据，而不是标准输出。
module	str	在 ad-hoc 模式下要由 Runner 调用的模块。
module_args	str	将提供给 ad-hoc 模式的模块参数。
host_pattern	str	在 ad-hoc 模式下要匹配的主机模式。
inventory	str或dict或list	通过覆盖 private_data_dir/inventory 中的清单目录/文件来指定特定的主机或主机列表。可以采用以下形式：
- private_data_dir 中的库存文件路径
- 支持 YAML/JSON 清单结构的本机 Python 字典
- INI 格式的文本 INI
- 空列表以禁用传递清单
ident	str	此调用 Runner 的标识符。将用于创建和命名包含结果的 artifact 目录。
role	str	要执行的角色名称。
roles_path	dict或list	要分配给 ANSIBLE_ROLES_PATH 的目录或目录列表。
passwords	dict	一个字典，包含在处理 Ansible 输出时使用的密码提示模式和响应值。还将从 private_data_dir 中的 env/passwords 中读取密码。
settings	dict	一个字典，包含 ansible-runner 运行时环境的设置值。这些设置还将从 private_data_dir 中的 env/settings 中读取。
suppress_env_files	bool	禁用写入可能包含敏感信息的 env 文件。
project_dir	str	playbook 内容的路径，默认为 private_data_dir 中的 'project'。
timeout	int	以秒为单位的超时值，将在执行命令时传递给 pexpect 或 subprocess 调用（基于选择的 runner_mode）。如果触发超时，它将强制取消执行。
streamer	str	可选地以流式传输管道的一个步骤调用 ansible-runner。
_input	io.FileIO	用于流式传输管道输入的可选项文件或类似文件的对象。
_output	io.FileIO	用于流式传输管道输出的可选项文件或类似文件的对象。
process_isolation	bool	启用进程隔离，使用容器引擎（例如 podman）或沙盒（例如 bwrap）。
process_isolation_executable	str	用于隔离执行的进程隔离可执行文件或容器引擎（默认：podman）。
process_isolation_path	str	隔离的 playbook 运行将用于暂存的路径。（默认：/tmp）
process_isolation_hide_paths	str或list	系统中应隐藏 playbook 运行的一路径或多路径。
process_isolation_show_paths	str或list	系统中应暴露给 playbook 运行的一路径或多路径。
process_isolation_ro_paths	str或list	系统中应以只读方式暴露给 playbook 运行的一路径或多路径。
container_image	str	在运行 ansible 任务时要使用的容器镜像（默认：quay.io/ansible/ansible-runner:devel）
container_volume_mounts	list	以 'host_dir:/container_dir' 形式的绑定挂载列表。 （默认：None）
container_options	list	要传递给执行引擎的容器选项列表。
directory_isolation_base_path	str	一个可选路径，将用作临时目录的基本路径，项目内容将被复制到此位置，然后在此位置作为工作目录进行 playbook 执行。
fact_cache	str	用于 'jsonfile' 类型事实缓存的子目录的名称，该子目录位于 artifacts 目录中。
fact_cache_type	str	要使用的事实缓存类型。默认为 'jsonfile'。
omit_event_data	bool	省略额外的 ansible 事件数据，但仍包括 stdout 和事件。
only_failed_event_data	bool	除非事件失败，否则省略额外的 ansible 事件数据，但仍包括 stdout 和事件。
check_job_event_data	bool	检查作业事件数据是否完全生成。如果事件数据未完全生成且值为 'True'，则会引发 'AnsibleRunnerException' 异常，如果设置为 'False'，则记录一条调试消息并继续执行。默认值为 'False'。
"""
import os.path
import shutil

from ansible_runner import run_command, RunnerConfig, Runner, run


def callback_status_handler(data, runner_config):
    """
        处理回调状态数据的函数
    :param data: 包含任务状态信息的字典，例如任务的当前状态、执行命令的详细信息等。
    :param runner_config: 运行器配置的字典，包含环境变量、工作目录等配置信息。
    :return:
    """
    print("status_handler-data:", data)
    # status_handler-data: {'status': 'starting', 'runner_ident': 'c1d2a174-6dbc-4a03-baaa-e6ec6d737f62', 'command': ['ansible', '-i', '/Users/zqqzqq/ansible/hosts.ini', '-m', 'command', '-a', 'ls', 'all'], 'env': {'DATAGRIP_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/datagrip.vmoptions', 'PATH': '/Users/zqqzqq/01_project/03_drf/drf_env/bin:/usr/local/mysql-8.0.33-macos13-x86_64/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/Library/Frameworks/Python.framework/Versions/3.11/bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/Applications/VMware Fusion.app/Contents/Public:/usr/local/go/bin', 'MANPATH': '/opt/homebrew/share/man::', 'PYCHARM_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/pycharm.vmoptions', 'WEBSTORM_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/webstorm.vmoptions', 'CLION_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/clion.vmoptions', 'JETBRAINSCLIENT_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/jetbrainsclient.vmoptions', 'HOMEBREW_PREFIX': '/opt/homebrew', 'GATEWAY_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/gateway.vmoptions', 'COMMAND_MODE': 'unix2003', 'PS1': '(drf_env) ', 'GOLAND_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/goland.vmoptions', 'IDEA_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/idea.vmoptions', 'RIDER_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/rider.vmoptions', 'RUBYMINE_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/rubymine.vmoptions', 'JETBRAINS_CLIENT_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/jetbrains_client.vmoptions', 'DEVECOSTUDIO_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/devecostudio.vmoptions', 'LOGNAME': 'zqqzqq', 'HOMEBREW_REPOSITORY': '/opt/homebrew', 'STUDIO_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/studio.vmoptions', 'XPC_SERVICE_NAME': 'application.com.jetbrains.pycharm.10912824.10913506', 'PWD': '/Users/zqqzqq/01_project/03_drf/drf/utils/ansible', 'PYCHARM_HOSTED': '1', 'INFOPATH': '/opt/homebrew/share/info:', 'PYCHARM_DISPLAY_PORT': '63342', '__CFBundleIdentifier': 'com.jetbrains.pycharm', 'PYTHONPATH': '/Users/zqqzqq/01_project/03_drf/drf:/Users/zqqzqq/01_project/03_drf/drf/apps:/Applications/PyCharm.app/Contents/plugins/python/helpers/pycharm_matplotlib_backend:/Applications/PyCharm.app/Contents/plugins/python/helpers/pycharm_display', 'SHELL': '/bin/zsh', 'APPCODE_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/appcode.vmoptions', 'PYTHONIOENCODING': 'UTF-8', 'HOMEBREW_BOTTLE_DOMAIN': 'https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles', 'OLDPWD': '/', 'HOMEBREW_CELLAR': '/opt/homebrew/Cellar', 'USER': 'zqqzqq', 'TMPDIR': '/var/folders/zd/bz67x_zs243cp5g3rc1x6k540000gn/T/', 'DATASPELL_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/dataspell.vmoptions', 'SSH_AUTH_SOCK': '/private/tmp/com.apple.launchd.95BtPwMPOf/Listeners', 'PYCHARM_INTERACTIVE_PLOTS': '1', 'VIRTUAL_ENV': '/Users/zqqzqq/01_project/03_drf/drf_env', 'XPC_FLAGS': '0x0', 'PYTHONUNBUFFERED': '1', 'WEBIDE_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/webide.vmoptions', '__CF_USER_TEXT_ENCODING': '0x1F5:0x19:0x34', 'PHPSTORM_VM_OPTIONS': '/Users/zqqzqq/02_software/ActivationCodes/ja-netfilter-all/vmoptions/phpstorm.vmoptions', 'LC_CTYPE': 'zh_CN.UTF-8', 'IDEA_INITIAL_DIRECTORY': '/', 'HOME': '/Users/zqqzqq', 'ANSIBLE_CALLBACK_PLUGINS': '/Users/zqqzqq/01_project/03_drf/drf_env/lib/python3.11/site-packages/ansible_runner/display_callback/callback', 'ANSIBLE_LOAD_CALLBACK_PLUGINS': '1', 'AD_HOC_COMMAND_ID': '1', 'ANSIBLE_STDOUT_CALLBACK': 'awx_display', 'ANSIBLE_RETRY_FILES_ENABLED': 'False', 'ANSIBLE_HOST_KEY_CHECKING': 'False', 'AWX_ISOLATED_DATA_DIR': '/Users/zqqzqq/ansible/artifacts/c1d2a174-6dbc-4a03-baaa-e6ec6d737f62', 'ANSIBLE_CACHE_PLUGIN': 'jsonfile', 'ANSIBLE_CACHE_PLUGIN_CONNECTION': '/Users/zqqzqq/ansible/artifacts/c1d2a174-6dbc-4a03-baaa-e6ec6d737f62/fact_cache', 'RUNNER_OMIT_EVENTS': 'False', 'RUNNER_ONLY_FAILED_EVENTS': 'False'}, 'cwd': '/Users/zqqzqq/ansible'}
    print("status_handler-runner_config:", runner_config)


def callback_artifacts_handler(artifacts_dir):
    """
        处理回调时的工件（artifacts）目录。
    :param artifacts_dir: 字符串，表示工件目录的路径
    :return:
    """
    print("artifacts_handler:", artifacts_dir)


def callback_cancel_callback():
    """
        执行取消操作的回调函数
    :return:
    """
    print("cancel_callback")


def callback_finished_callback(runner):
    """
        当回调任务完成时被调用的回调函数
    :param runner: 一个包含标准输出的运行器对象，用于获取任务的输出结果
    :return:
    """
    print("finished_callback:", runner.stdout.read(), runner.stdout.read())


class AnsibleRunnerManager:
    """
        会在private_data_dir这个目录下生成artifacts临时文件
    """

    def __init__(self,
                 private_data_dir,
                 inventory,
                 status_handler=None,
                 artifacts_handler=None,
                 cancel_callback=None,
                 finished_callback=None
                 ):
        """
        :param private_data_dir: 私有数据目录的路径，用于存储和访问私有数据
        :param inventory: 要么指定主机的路径，要么直接写主机，然后在private_data_dir/inventory/hosts中写主机
        :param status_handler: callback_status_handler 直接传这个或者其他另外写个回调函数
        :param artifacts_handler: callback_artifacts_handler 直接传这个或者另外写个其他回调函数
        :param cancel_callback: callback_cancel_callback 直接传这个或者另外写个其他回调函数
        :param finished_callback: callback_finished_callback 直接传这个或者另外写个其他回调函数
        """
        self.private_data_dir = private_data_dir
        self.inventory = inventory
        self.rotate_artifacts = 1
        self.status_handler = status_handler
        self.artifacts_handler = artifacts_handler
        self.cancel_callback = cancel_callback
        self.finished_callback = finished_callback

    def cleanup_artifacts(self):
        """
            删除生成的临时文件
        :return:
        """
        artifacts_dir = os.path.join(self.private_data_dir, "artifacts")
        if os.path.exists(artifacts_dir):
            shutil.rmtree(artifacts_dir)

    def run_adhoc(self, module, module_args, host_pattern="all"):
        """
            执行临时任务，使用指定的模块和参数在匹配的主机上运行
        :param module: 指定要运行的模块名称
        :param module_args: 传递给模块的参数，格式为字符串
        :param host_pattern:用于匹配要运行模块的主机的模式，默认为"all"，表示所有主机
        :return:返回一个元组，包括操作是否成功（True/False）和执行结果（标准输出或标准错误）
        """
        res = run(
            private_data_dir=self.private_data_dir,
            inventory=self.inventory,
            module=module,
            module_args=module_args,
            host_pattern=host_pattern,
            rotate_artifacts=self.rotate_artifacts,
            status_handler=self.status_handler,
            artifacts_handler=self.artifacts_handler,
            cancel_callback=self.cancel_callback,
            finished_callback=self.finished_callback
        )
        if res.status == "successful":
            return True, res.stdout.read()
        else:
            return False, res.stderr.read()

    def run_adhoc_by_inventory(self, module, module_args, inventory):
        """
            使用给定的清单信息运行临时任务。
        :param module:指定要运行的模块名称
        :param module_args:传递给模块的参数字符串
        :param inventory: 清单信息，指定哪些主机上运行模块
            {
                "test": {
                    "hosts": {
                        "host01": {
                            "ansible_host": "192.168.1.3",
                            "ansible_port": 22,
                            "ansible_user": "root",
                            "ansible_ssh_pass": "111111"
                        },
                    }
                }
            }
        :return:一个元组，包含操作是否成功（True/False）以及操作的结果（标准输出或标准错误）
        """
        res = run(
            private_data_dir=self.private_data_dir,
            module=module,
            module_args=module_args,
            inventory=inventory,
            rotate_artifacts=self.rotate_artifacts,
            status_handler=self.status_handler,
            artifacts_handler=self.artifacts_handler,
            cancel_callback=self.cancel_callback,
            finished_callback=self.finished_callback
        )
        if res.status == "successful":
            return True, res.stdout.read()
        else:
            return False, res.stderr.read()

    def run_playbook(self, playbook):
        """
            执行Ansible playbook，并返回执行结果
        :param playbook: 剧本路径，可以是相对与private_data_dir的路径。
                        或者是绝对路径
        :return:
            一个元组，包括执行状态（True为成功，False为失败）和执行输出（标准输出或标准错误）
        """
        res = run(
            private_data_dir=self.private_data_dir,
            inventory=self.inventory,
            playbook=playbook,
            rotate_artifacts=self.rotate_artifacts,
            status_handler=self.status_handler,
            artifacts_handler=self.artifacts_handler,
            cancel_callback=self.cancel_callback,
            finished_callback=self.finished_callback

        )
        if res.status == "successful":
            return True, res.stdout.read()
        else:
            return False, res.stderr.read()

    def run_playbook_by_config(self, config=None):
        """
            根据配置运行playbook
        :param config:
            {
                "playbook":"",
                ... 可以查看源码
            }
        :return:
        """
        if config is None:
            config = {}
        config.update({"private_data_dir": self.private_data_dir,
                       "inventory": self.inventory})
        rc = RunnerConfig(**config)
        rc.prepare()
        r = Runner(config=rc)
        state, _ = r.run()
        if state == "successful":
            return True, r.stdout.read()
        return False, r.stderr.read()

    def run_command_by_cmd(self, executable_cmd, cmdline_args=None):
        """
            函数来执行一个外部命令，并返回命令的输出和错误信息
        :param executable_cmd: 执行的命令字符串
        :param cmdline_args: 命令行参数的列表，可选，默认为 None。
        :return:
        """
        out, err, _ = run_command(
            executable_cmd=executable_cmd,
            cmdline_args=cmdline_args,
            rotate_artifacts=self.rotate_artifacts,
            status_handler=self.status_handler,
            artifacts_handler=self.artifacts_handler,
            cancel_callback=self.cancel_callback,
            finished_callback=self.finished_callback
        )
        return out, err


if __name__ == '__main__':
    private_data_dir = '/Users/zqqzqq/ansible'
    playbook = '/Users/zqqzqq/ansible/playbook/ping_book.yml'
    playbook = "playbook/ping_book.yml"
    runner = AnsibleRunnerManager(private_data_dir, "/Users/zqqzqq/ansible/hosts.ini",
                                  status_handler=callback_status_handler, finished_callback=callback_finished_callback)
    print(runner.run_adhoc(module="command", module_args="ls"))
    # print(runner.run_playbook(playbook=playbook))

    # config = {
    #     "playbook": playbook
    # }
    # print(runner.run_playbook_by_config(config))

    # print(runner.run_command_by_cmd("ls -l"))
    # print(runner.run_command_by_cmd("ls",cmdline_args=['-l']))
    # print(runner.run_command_by_cmd("ansible-doc",cmdline_args=['ping']))
    # print(runner.run_command_by_cmd("ansible-playbook",cmdline_args=['/Users/zqqzqq/ansible/playbook/ping_book.yml']))

import json

from ansible_runner import Runner, run_command


class AnsibleRunnerManager:
    def __init__(self, private_data_dir, host_list=None, inventory_path=None, playbook_path=None):
        self.private_data_dir = private_data_dir
        self.host_list = host_list
        self.inventory = inventory_path
        self.playbook_path = playbook_path

    def run_adhoc(self, module, module_args, host_pattern='all'):
        """
        run_adhoc: 执行Ad-Hoc命令。
        """
        runner = Runner(
            private_data_dir=self.private_data_dir,
            host_pattern=host_pattern,
            module=module,
            module_args=module_args,
        )
        return runner.run()

    def run_playbook(self, extra_vars=None):
        """
        run_playbook: 运行Ansible playbook
        """
        runner = Runner(
            private_data_dir=self.private_data_dir,
            playbook=self.playbook_path,
            inventory=self.host_list,
            extravars=extra_vars,
        )
        return runner.run()

    def get_job_status(self, job_id):
        """
        get_job_status: 查询作业状态
        """
        result = run_command(f"ansible-runner status {self.private_data_dir} {job_id}")
        return result['stdout'].strip()

    def get_job_artifacts(self, job_id):
        """
        get_job_artifacts: 获取作业的所有工件（包括日志、标准输出、事实缓存等）
        """
        result = run_command(f"ansible-runner artifacts {self.private_data_dir} {job_id}")
        return json.loads(result['stdout'])

    def get_job_out(self, job_id):
        """
            获取作业的输出
        """
        artifacts = self.get_job_artifacts(job_id)
        out = {
            "stdout": artifacts['stdout'],
            "stderr": artifacts['stderr']
        }
        return out

    def clean_up(self):
        """
        clean_up: 清理Ansible Runner产生的临时文件和目录
        """
        run_command(f"ansible-runner cleanup {self.private_data_dir}")

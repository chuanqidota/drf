import subprocess


class SubprocessManager:
    """
        执行系统命令
    """

    def __init__(self, command):
        self.command = command

    def run(self, shell=True, capture_output=True, text=True, check=False, timeout=10):
        """
            执行命令
        :param shell: True 命令可以为字符串，False 必须为列表
        :param capture_output: True结果可以拿到，False只会在终端输出
        :param text: 文本流
        :param check: 如果check参数的值是True，且执行命令的进程以非0状态码退出，则会抛出一个CalledProcessError的异常
        :param timeout: 超时时间
        :return:
        """
        result = subprocess.run(self.command,
                                shell=shell,
                                text=text,
                                check=check,
                                timeout=timeout,
                                capture_output=capture_output
                                )
        return {
            "status": True if result.returncode == 0 else False,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    def popen(self, cwd=None, env=None, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
              stderr=subprocess.PIPE, text=True, timeout=10):
        """
            细致的参数 执行命令
        :param cwd: 工作目录:执行命令前就
        :param env: 环境变量 {"a":"b"}
        :param shell:
        :param stdin:
        :param stdout:
        :param stderr:
        :param text:
        :param timeout:
        :return:
        """
        with subprocess.Popen(self.command,
                              cwd=cwd,
                              env=env,
                              shell=shell,
                              stdin=stdin,
                              stdout=stdout,
                              stderr=stderr,
                              text=text) as process:
            stdout, stderr = process.communicate(timeout=timeout)
            return {
                "status": True if process.returncode == 0 else False,
                "stdout": stdout,
                "stderr": stderr
            }

    def input(self, category="bash", timeout=10):
        """
            输入的方式 执行命令
        :param category: bash/python2/python3
        :param timeout:
        :return:
        """
        if category == "bash":
            command = ["/bin/bash"]
        elif category == "python2":
            command = ["python2"]
        elif category == "python3":
            command = ["python3"]
        else:
            return

        # 启动子进程，并设置标准输入和标准输出
        with subprocess.Popen(command,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE
                              ) as process:
            # 向子进程发送输入数据
            process.stdin.write(self.command.encode())
            process.stdin.flush()

            stdout, stderr = process.communicate(timeout=timeout)
            process.stdin.close()

            return {
                "status": True if process.returncode == 0 else False,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8")
            }


if __name__ == '__main__':
    # print(SubprocessManager("cd && ls").run())

    # 切换目录
    # print(SubprocessManager("ls").popen(cwd="/Users/jinang/01_software"))

    # 环境变量
    # print(SubprocessManager("echo $aaa").popen(env={"aaa": "bbb"}))

    # 输入-bash
    # print(SubprocessManager("echo 'Hello, this is some input data'").input("bash"))

    # 输入-python2
    # print(SubprocessManager("print 'python2'").input("python2"))

    # 输入-python3
    # print(SubprocessManager("print('python3')").input("python3"))
    pass

import time

import paramiko


class RemoteSSHExecutor:
    def __init__(self, host, user, password, port=22):
        """
            初始化RemoteSSHExecutor对象。
        :param host: 远程主机地址
        :param user: 登录用户名
        :param password: 登录密码
        :param port: SSH端口，默认为22
        """
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        """
            建立到远程服务器的SSH连接
        :return:
        """
        self.client.connect(self.host, port=self.port, username=self.user, password=self.password)

    def disconnect(self):
        """
            断开与远程服务器的SSH连接
        :return:
        """
        self.client.close()

    def execute_command(self, command, timeout=None):
        """
            执行远程命令并获取输出和错误信息
        :param command:
        :return: 标准输出，错误输出
        """
        _, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        return output, error

    def execute_command_with_transport(self, command):
        """
            我们首先创建一个paramiko.Transport对象并连接到远程服务器。
            接着，通过transport.open_session()打开一个会话通道，并在该通道上执行命令。
            使用channel.recv()和channel.recv_stderr()接收命令输出和错误信息。
            由于命令可能需要一段时间才能完成执行，我们使用循环和time.sleep()来周期性地检查输出和错误，
            直到channel.exit_status_ready()返回True，表示命令已执行完毕。最后，获取命令退出状态并关闭传输连接
        :param command:
        :return:
        """
        transport = self.client.get_transport()
        channel = transport.open_session()
        channel.exec_command(command)
        output = channel.recv(1024).decode('utf-8')
        error = channel.recv_stderr(1024).decode('utf-8')
        while not channel.exit_status_ready():
            time.sleep(0.5)  # 可以根据实际情况调整等待时间
            output += channel.recv(1024).decode('utf-8')
            error += channel.recv_stderr(1024).decode('utf-8')

        exit_status = channel.recv_exit_status()
        if exit_status != 0:
            raise Exception(f"Command exited with non-zero status: {exit_status}")
        transport.close()

        return output, error

    def upload_file(self, local_path, remote_path):
        """
            将本地文件上传到远程服务器指定路径
        :param local_path: 本地路径
        :param remote_path: 远程路径
        :return:
        """
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def stream_upload_file(self, file_obj, remote_path):
        """
            将文件流上传到远程服务器指定路径
        :param file_obj: 文件对象
        :param remote_path: 远程路径
        :return:
        """
        sftp = self.client.open_sftp()
        sftp.putfo(file_obj, remote_path)
        sftp.close()

    def download_file(self, remote_path, local_path):
        """
            从远程服务器下载文件到本地指定路径
        :param remote_path: 远程服务器上的文件路径
        :param local_path: 本地的目标路径
        :return:
        """
        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    def stream_download_file(self, remote_path, file_obj):
        """
            从远程服务器下载文件到本地文件对象
        :param remote_path: 远程服务器上的文件路径
        :param file_obj: 本地文件对象
        :return:
        """
        sftp = self.client.open_sftp()
        sftp.getfo(remote_path, file_obj)
        sftp.close()

    def list_file(self, remote_path):
        """
            列出远程服务器指定路径下的文件列表
        :param remote_path:
        :return:
        """
        sftp = self.client.open_sftp()
        file_list = sftp.listdir(remote_path)
        sftp.close()
        return file_list


if __name__ == '__main__':
    # 使用示例：
    executor = RemoteSSHExecutor("your_server_ip", "your_username", "your_password")
    executor.connect()

    # 执行命令
    _command = "ls -l /path/to/directory"
    _output, _error = executor.execute_command(_command)
    print(f"Command Output:\n{_output}")
    print(f"Error (if any):\n{_error}")

    # 上传文件
    local_file = "/local/path/to/file.txt"
    remote_file = "/remote/path/on/server/file.txt"
    executor.upload_file(local_file, remote_file)

    executor.disconnect()

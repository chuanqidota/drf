from fabric import Connection, Config
from invoke.exceptions import UnexpectedExit


class RemoteManager:
    def __init__(self, host, user='root', password=None, key_file=None):
        self.config = Config(overrides={'sudo': {'password': password}})  # 示例sudo密码配置
        self.conn = None
        self.host = host
        self.user = user
        self.key_file = key_file

    def connect(self):
        """建立与远程服务器的连接。"""
        if not self.conn:
            self.conn = Connection(
                host=self.host,
                user=self.user,
                connect_kwargs={'key_filename': self.key_file} if self.key_file else {},
                config=self.config
            )

    def disconnect(self):
        """断开与远程服务器的连接。"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def run_command(self, command, sudo=False, hide=True):
        """
        在远程服务器上执行命令。
        :param command: 要执行的命令字符串。
        :param sudo: 是否以sudo权限执行。
        :param hide: 是否隐藏命令输出。
        :return: 命令的输出或异常信息。
        """
        try:
            result = self.conn.sudo(command) if sudo else self.conn.run(command, hide=hide)
            if result.failed:
                return f"Command '{command}' failed with exit code {result.exited}. Output: {result.stdout}"
            return result.stdout.strip() if result.stdout else "Command executed successfully."
        except UnexpectedExit as e:
            return f"An unexpected error occurred while executing '{command}'. Exit code: {e.result.exited}"

    def upload_file(self, local_path, remote_path):
        """
        将本地文件上传到远程服务器。
        :param local_path: 本地文件路径。
        :param remote_path: 远程文件存放路径。
        """
        try:
            self.conn.put(local_path, remote_path)
            return f"File uploaded successfully to {remote_path}"
        except Exception as e:
            return f"Failed to upload file: {str(e)}"

    def download_file(self, remote_path, local_path):
        """
        从远程服务器下载文件到本地。
        :param remote_path: 远程文件路径。
        :param local_path: 本地保存路径。
        """
        try:
            self.conn.get(remote_path, local_path)
            return f"File downloaded successfully to {local_path}"
        except Exception as e:
            return f"Failed to download file: {str(e)}"


# 使用示例
if __name__ == "__main__":
    manager = RemoteManager(host='your_server_ip',
                            user='your_username',
                            password="your_password",
                            key_file='/path/to/ssh/key')
    manager.connect()

    # 执行命令
    print(manager.run_command("ls -l", sudo=False))

    # 上传文件
    print(manager.upload_file("/local/path/to/file.txt", "/remote/path/to/file.txt"))

    # 下载文件
    print(manager.download_file("/remote/path/to/file.txt", "/local/download/path/file.txt"))

    # 断开连接
    manager.disconnect()

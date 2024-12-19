import traceback
from io import BytesIO
import mimetypes

import boto3


class S3Manager:
    """
        S3处理上传下载文件
    """

    def __init__(self, access_key_id, secret_access_key, endpoint_url, bucket_name):
        self.access_key_id = access_key_id  # id
        self.secret_access_key = secret_access_key  # key
        self.endpoint_url = endpoint_url  # endpoint
        self.service_name = "s3"
        self.bucket_name = bucket_name  # 桶名字

        self.client = self.create_client()

    def create_client(self):
        """
            客户端创建
        :return:
        """
        client = boto3.client(self.service_name, aws_access_key_id=self.access_key_id,
                              aws_secret_access_key=self.secret_access_key,
                              endpoint_url=self.endpoint_url)

        return client

    def upload_file(self, key, file_path):
        """
            本地文件上传
        :param key: key
        :param file_path: 本地文件路径-绝对
        :return: 对象key
        """
        try:
            if not key:
                key = os.path.basename(file_path)
            self.client.upload_file(file_path, self.bucket_name, key)
            return True
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return False

    def download_file(self, key, file_path):
        """
            下载文件
        :param key: 对象key
        :param file_path: 文件路径
        :return:
        """
        try:
            self.client.download_file(self.bucket_name, key, file_path)
            return True
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return False

    def delete_file(self, key):
        """
            删除文件
        :param key: 对象 key
        :return:
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return False

    def upload_file_buffer(self,file_path,key=None):
        """
            流文件上传
            这里一定要特别注意
        :param key: key
        :param file_path: 文件路径
        :return: 对象key
        """
        try:
            if not key:
                key = os.path.basename(file_path)
            content_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, "r") as f:
                data_stream = BytesIO(f.read())
                # 上传流文件到S3存储桶
                self.client.upload_fileobj(data_stream, self.bucket_name, key, ExtraArgs={'ContentType': content_type})
                return True
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return False

    def download_file_buffer(self, key):
        """
            流下载文件
        :param key: 对象key
        :return: 文件流
        """
        try:
            # 创建一个BytesIO流对象来保存下载的数据
            data_stream = BytesIO()
            # 下载S3对象到流文件
            self.client.download_fileobj(self.bucket_name, key, data_stream)
            # 将流文件的内容读取到一个变量中
            downloaded_data = data_stream.getvalue()
            return True, downloaded_data
        except Exception as e:
            print(traceback.format_exc(), repr(e))
            return False, None
        # view中的相应代码
        # response = Response(file_data, content_type='application/octet-stream')
        # response.headers['Content-Disposition'] = f'attachment; filename={file_name}'

from fdfs_client.client import Fdfs_client


# fdfs-client-py3==1.0.0

class FastDfsHandle(object):
    """
        fastdfs相关处理
    """

    def __init__(self, conf="./fdfs_tracker.conf"):
        self.client = Fdfs_client(client=conf)

    def upload_file_buffer(self, file):
        """
            上传文件-文件流-不需要本地保存文件
        :param file: 文件
        :return: 远程文件id
        """
        try:
            ret = self.client.upload_by_buffer(file.read())
            """
                {
                    'Group name': 'group1',
                    'Remote file_id': 'group1/000/00/13/CrE2MmVJ2yeIV81rAAABLP4rmOwAABBeQCb6qgAAAFE6910957',
                    'Status': 'Upload successed.',
                    'Local file name': '',
                    'Uploaded size': '300B',
                    'Storage IP': '10.177.54.50'
                }
            """
            if ret.get('Status') == 'Upload successed.':
                remote_file_id = ret.get('Remote file_id')
                return True, remote_file_id
            return False, ret
        except Exception as e:
            return False, repr(e)

    def download_file_buffer(self, remote_file_id):
        """
            下载文件-文件流
        :param remote_file_id:远程文件id
        :return: 文件流
        """
        try:
            ret = self.client.download_to_buffer(remote_file_id.encode("utf-8"))
            file_data = ret.get('Content')
            return True, file_data
        except Exception as e:
            return False, repr(e)

    def delete_file(self, remote_file_id):
        """
            删除远程文件
        :param remote_file_id: 远程文件id
        :return:
        """
        try:
            ret = self.client.delete_file(remote_file_id=remote_file_id.encode("utf-8"))
            if "Delete file successed." in ret:
                return True, "删除成功"
            else:
                return False, "删除失败"
        except Exception as e:
            return False, repr(e)

    def upload_file(self, file_path):
        """
            上传文件
        :param file_path: 本地文件路径
        :return:
        """
        try:
            ret = self.client.upload_by_filename(file_path)
            if ret.get('Status') == 'Upload successed.':
                remote_file_id = ret.get('Remote file_id')
                return True, remote_file_id
            return False, ret
        except Exception as e:
            return False, repr(e)

    def download_file(self, save_file, remote_file_id):
        """
            下载文件
        :param save_file:保存在本地的文件名
        :param remote_file_id: 远程id
        :return:
        """
        try:
            ret = self.client.download_to_file(save_file, remote_file_id.encode('utf-8'))
            file_data = ret.get('Content')
            return True, file_data
        except Exception as e:
            return False, repr(e)

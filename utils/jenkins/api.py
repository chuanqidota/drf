from jenkinsapi import jenkins
from django.conf import settings
from xml.etree import ElementTree as ET


class XmlParse:
    def __init__(self, config_xml):
        with open(config_xml, 'r') as f:
            self.xml_root = ET.XML(f.read())

    def replace_flow(self, **kwargs):
        """
        替换xml(pipeline)模版文件内容
        job_description: job描述
        pipeline_git_url: 流水线文件git地址
        git_credential: git凭证ID
        groovy_script_git_path: groovy脚本地址
        """
        # 找元素
        desc = self.xml_root.find('description')
        definition = self.xml_root.find('definition')
        git_config = definition.find('scm').find('userRemoteConfigs').find('hudson.plugins.git.UserRemoteConfig')
        script_path = definition.find('scriptPath')
        # 替换
        desc.text = kwargs['job_description']
        git_config.find('url').text = kwargs['pipeline_git_url']
        git_config.find('credentialsId').text = kwargs['git_credential']
        script_path.text = kwargs['groovy_script_git_path']
        xml_bytes = ET.tostring(self.xml_root, encoding='utf-8')
        return xml_bytes


class JenkinsApi:
    """
    jenkins api 封装
    """
    def __init__(self, job_name=None):
        self.jen_cli = jenkins.Jenkins(settings.JENKINS_URL, username=settings.JENKINS_USERNAME,
                                       password=settings.JENKINS_PASSWORD, use_crumb=False, timeout=60)
        self.config_flow = './config/config_flow.xml'
        self.job_name = job_name

    def create_job(self, **kwargs):
        """
        创建JOB
        """
        x = XmlParse(self.config_flow)
        config = x.replace_flow(**kwargs)
        return self.jen_cli.create_job(self.job_name, config)

    def update_job(self, **kwargs):
        """
        更新JOB
        """
        x = XmlParse(self.config_flow)
        config = x.replace_flow(**kwargs)
        return self.jen_cli.get_job(self.job_name).update_config(config)

    def rename_job(self, new_job_name):
        """
        JOB重命名
        """
        return self.jen_cli.rename_job(self.job_name, new_job_name)

    def get_job_xml(self):
        """
        获取JOB的xml配置内容
        """
        url = self.jen_cli.get_job(self.job_name).get_config_xml_url()
        xml = self.jen_cli.requester.get_url(url)
        return xml.text

    def build_job(self, params=None):
        """
        触发构建
        """
        queue_item = self.jen_cli.jobs.build(self.job_name, params)
        running_queue_build = queue_item.block_until_building(delay=1)
        return running_queue_build.get_number()

    def build(self, build_number):
        """
        获取某次构建
        """
        return self.jen_cli.get_job(self.job_name).get_build(build_number)


def deploy(app, env, build_config):
    pass
from jenkinsapi import jenkins
from django.conf import settings
from xml.etree import ElementTree as ET
# jenkinsapi

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


from jenkinsapi.jenkins import Jenkins
import logging


class JenkinsClient:

    def __init__(self, url, username=None, password=None):
        """
        初始化Jenkins客户端
        :param url: Jenkins服务器URL
        :param username: Jenkins登录用户名（可选）
        :param password: Jenkins登录密码或API token（可选）
        """
        self.logger = logging.getLogger(__name__)
        self.client = Jenkins(url, username=username, password=password)

    def get_all_jobs(self):
        """
        获取所有作业的名称列表
        :return: 作业名称列表
        """
        jobs = self.client.get_jobs_list()
        return jobs

    def get_job_info(self, name):
        """
        获取指定作业的信息
        :param name: 作业名称
        :return: 作业信息字典
        """
        job = self.client.get_job(name)
        info = job.get_info()
        return info



    def get_job_config(self, name):
        """
        获取指定作业的XML配置
        :param name: 作业名称
        :return: 作业XML配置
        """
        job = self.client.get_job(name)
        xml = job.get_config()
        return xml

    def create_job(self, name, xml):
        """
        根据提供的XML配置创建新的Jenkins作业
        :param name: 新作业的名称
        :param xml: Jenkins作业的XML配置
        :return: 创建作业是否成功
        """
        try:
            self.client.create_job(name, xml)
            return True
        except Exception as e:
            return False

    def create_pipeline_job(self, name, pipeline_script):
        """
        创建Pipeline类型的Jenkins作业
        :param name: 新作业的名称
        :param pipeline_script: Jenkins Pipeline脚本内容 (Groovy语法)
        :return: 创建作业是否成功
        """
        pipeline_xml = f"""
           <flow-definition plugin="workflow-job@2.40">
             <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.93">
               <script>{pipeline_script}</script>
               <sandbox>true</sandbox>
             </definition>
             <triggers/>
             <disabled>false</disabled>
           </flow-definition>
           """
        return self._create_job_with_xml(name, pipeline_xml)

    def _create_job_with_xml(self, name, config_xml):
        """
        辅助方法：根据提供的XML配置创建作业
        :param name: 新作业的名称
        :param config_xml: Jenkins作业的XML配置
        :return: 创建作业是否成功
        """
        try:
            self.client.create_job(name, config_xml)
            self.logger.info(f"Job '{name}' created successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create job '{name}': {e}")
            return False

    def trigger_build(self, job_name, params=None):
        """
        触发指定作业的构建
        :param job_name: 作业名称
        :param params: 构建参数字典（可选）
        :return: 触发构建是否成功，以及构建编号
        """
        job = self.client[job_name]
        build_number = job.invoke(build_params=params)
        self.logger.info(f"Build triggered for '{job_name}', Build #{build_number}.")
        return True, build_number

    def get_build_status(self, job_name, build_number):
        """
        获取指定作业某次构建的状态
        :param job_name: 作业名称
        :param build_number: 构建编号
        :return: 构建状态（如'SUCCESS', 'FAILURE'等）
        """
        build = self.client[job_name].get_build(build_number)
        status = build.get_status()
        self.logger.info(f"Build #{build_number} of '{job_name}' has status: {status}.")
        return status


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 初始化Jenkins客户端
    jenkins_url = "http://127.0.0.1:8080"
    jenkins_username = "admin"
    jenkins_password = "1234"
    client = JenkinsClient(jenkins_url, username=jenkins_username, password=jenkins_password)

    # 获取所有作业名称
    print(client.get_all_jobs())
    print(client.get_job_config("http:/localhost:8080/项目-1"))

    # 创建新作业（这里需要提供一个有效的XML配置字符串）
    with open("./config.xml", 'r') as f:
        config_xml = ET.XML(f.read())
    xml_bytes = ET.tostring(config_xml, encoding='utf-8')
    success = client.create_job("new-job2", xml_bytes)
    # print("Job creation successful:", success)

    # 触发构建并获取状态（假设作业已存在）
    # success, build_num = client.trigger_build("existing-job", {"param1": "value1"})
    # print("Build triggered:", success, "Build Number:", build_num)

    # 查询构建状态
    # status = client.get_build_status("existing-job", build_num)
    # print("Build Status:", status)

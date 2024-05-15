"""
    python-jenkins==1.8.2
"""
from xml.etree import ElementTree

import jenkins


class JenkinsManager:
    def __init__(self, url, username, password):
        self.jenkins = jenkins.Jenkins(url, username=username, password=password)

    def create_view(self, view_name, xml=jenkins.EMPTY_VIEW_CONFIG_XML):
        """
            创建视图
        :param view_name:视图名称
        :param xml: 配置的xmL：默认
        :return:
        """
        self.jenkins.create_view(view_name, xml)

    def get_view_config(self, view_name):
        """
            获取视图配置
        :param view_name: 视图名称
        :return:
            <?xml version="1.1" encoding="UTF-8"?>
                <hudson.model.ListView>
                  <name>view-1</name>
                  <filterExecutors>false</filterExecutors>
                  <filterQueue>false</filterQueue>
                  <properties class="hudson.model.View$PropertyList"/>
                  <jobNames>
                    <comparator class="hudson.util.CaseInsensitiveComparator"/>
                  </jobNames>
                  <jobFilters/>
                  <columns>
                    <hudson.views.StatusColumn/>
                    <hudson.views.WeatherColumn/>
                    <hudson.views.JobColumn/>
                    <hudson.views.LastSuccessColumn/>
                    <hudson.views.LastFailureColumn/>
                    <hudson.views.LastDurationColumn/>
                    <hudson.views.BuildButtonColumn/>
                  </columns>
                  <recurse>false</recurse>
            </hudson.model.ListView>
        """
        return self.jenkins.get_view_config(view_name)

    def get_views(self):
        """
            获取所有视图
        :return:
            [{'_class': 'hudson.model.AllView', 'name': 'all', 'url': 'http://localhost:8080/'}, {'_class': 'hudson.model.ListView', 'name': 'view-1', 'url': 'http://localhost:8080/view/view-1/'}]
        """
        return self.jenkins.get_views()

    def delete_view(self, view_name):
        """
            删除视图
        :param view_name: 视图名称
        :return:
        """
        self.jenkins.delete_view(view_name)

    def get_view_jobs(self, view_name):
        """
            获取视图中的作业列表
        :param view_name: 视图名称
        :return:
        """
        return self.jenkins.get_jobs(view_name=view_name)

    def create_job(self, job_name, xml=jenkins.EMPTY_CONFIG_XML):
        """
            创建job
        :param job_name: job名称
        :param xml: 配置
        :return:
        """
        self.jenkins.create_job(job_name, xml)

    def get_all_jobs(self):
        """
            获取所有的job
        :return:
        """
        return self.jenkins.get_all_jobs()

    def get_job_info(self, job_name):
        """
            根据job名称获取job信息
        :param job_name:job名称
        :return:
                {'_class': 'hudson.model.FreeStyleProject', 'actions': [{}, {}, {}, {}, {'_class': 'org.jenkinsci.plugins.displayurlapi.actions.JobDisplayAction'}, {'_class': 'com.cloudbees.plugins.credentials.ViewCredentialsAction'}], 'description': None, 'displayName': 'job-name2', 'displayNameOrNull': None, 'fullDisplayName': 'job-name2', 'fullName': 'job-name2', 'name': 'job-name2', 'url': 'http://localhost:8080/job/job-name2/', 'buildable': True, 'builds': [], 'color': 'notbuilt', 'firstBuild': None, 'healthReport': [], 'inQueue': False, 'keepDependencies': False, 'lastBuild': None, 'lastCompletedBuild': None, 'lastFailedBuild': None, 'lastStableBuild': None, 'lastSuccessfulBuild': None, 'lastUnstableBuild': None, 'lastUnsuccessfulBuild': None, 'nextBuildNumber': 1, 'property': [], 'queueItem': None, 'concurrentBuild': False, 'disabled': False, 'downstreamProjects': [], 'labelExpression': None, 'scm': {'_class': 'hudson.scm.NullSCM'}, 'upstreamProjects': []}
        """
        return self.jenkins.get_job_info(job_name)

    def get_job_config(self, job_name):
        """
            获取job配置
        :param job_name: job名称
        :return:
            <?xml version="1.0" encoding="UTF-8"?><project>
              <keepDependencies>false</keepDependencies>
              <properties/>
              <scm class="jenkins.scm.NullSCM"/>
              <canRoam>true</canRoam>
              <disabled>false</disabled>
              <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
              <triggers class="vector"/>
              <concurrentBuild>false</concurrentBuild>
              <builders/>
              <publishers/>
              <buildWrappers/>
            </project>
        """
        return self.jenkins.get_job_config(job_name)

    def reconfig_job(self, job_name, xml=jenkins.RECONFIG_XML):
        """
            重新配置job
        :param job_name: job名称
        :param xml: xml配置文件
        :return:
        """
        self.jenkins.reconfig_job(job_name, xml)

    def job_exists(self, job_name):
        """
            判断job是否存在
        :param job_name: job名称
        :return:
        """
        return self.jenkins.job_exists(job_name)

    def disable_job(self, job_name):
        """
            禁用job
        :param job_name: job名称
        :return:
        """
        return self.jenkins.disable_job(job_name)

    def enable_job(self, job_name):
        """
            启用job
        :param job_name: job名称
        :return:
        """
        return self.jenkins.enable_job(job_name)

    def delete_job(self, job_name):
        """
            删除job
        :param job_name: job名称
        :return:
        """
        return self.jenkins.delete_job(job_name)

    def build_job(self, job_name, parameters=None):
        """
            构建job
        :param job_name: job名称
        :param parameters: 参数
        :return:
        """
        return self.jenkins.build_job(job_name, parameters)

    def stop_build(self, job_name, number):
        """
            停止构建
        :param job_name: job名称
        :param number: 构建编号
        :return:
        """
        return self.jenkins.stop_build(job_name, number)

    def delete_build(self, job_name, number):
        """
            删除构建
        :param job_name: job名称
        :param number: 构建编号
        :return:
        """
        return self.jenkins.delete_build(job_name, number)

    def get_running_builds(self):
        """
            获取正在构建的job
        :return:
        """
        return self.jenkins.get_running_builds()

    def get_last_build_info(self, job_name):
        """
            获取最后一次构建的编号
        :param job_name:
        :return:
        """
        job_info = self.get_job_info(job_name)
        return self.get_build_info(job_name, job_info['lastBuild']['number'])

    def set_next_build_number(self, job_name, number):
        """
            设置下次构建的编号
        :param job_name: job名称
        :param number: 构建的编号
        :return:
        """
        return self.jenkins.set_next_build_number(job_name, number)

    def get_build_info(self, job_name, build_number):
        """
            获取构建信息
        :param job_name: job名称
        :param build_number: 构建编号
        :return:
        """
        return self.jenkins.get_build_info(job_name, build_number)

    def check_jenkinsfile_syntax(self, jenkinsfile):
        """
            校验jenkinsfile语法
        :param jenkinsfile: Jenkinsfile text, ``str``
        :return:
        """
        return self.jenkins.check_jenkinsfile_syntax(jenkinsfile)

    @staticmethod
    def _parse_xml_root_str(config_xml):
        """
            字符串的配置文件解析
        :param config_xml: 字符串的配置文件
        :return:
        """
        xml_root = ElementTree.fromstring(config_xml)
        return xml_root

    @staticmethod
    def _parse_xml_root_file(config_xml):
        """
            文本的配置文件解析
        :param config_xml:
        :return:
        """
        with open(config_xml, 'r') as f:
            xml_root = ElementTree.XML(f.read())
        return xml_root

    @staticmethod
    def replace_xml(xml_root, **kwargs):
        """
            替换xml文件中的元素信息
        :param xml_root: self._parse_xml_root_str 或 self._parse_xml_root_file 解析的根路径
        :param kwargs: 需要的配置
        :return:
        """
        # 更改方法
        # root.find("").text = kwargs.get("")
        updated_config_xml = ElementTree.tostring(xml_root, encoding="utf-8").decode("utf-8")
        return updated_config_xml





if __name__ == "__main__":
    # 示例用法
    jenkins_url = "http://localhost:8080"
    jenkins_username = "admin"
    jenkins_password = "1234"

    manager = JenkinsManager(jenkins_url, jenkins_username, jenkins_password)
    # print(manager.create_view("view-1"))
    # print(manager.get_view_config("view-1"))
    # print(manager.get_views())
    # print(manager.delete_view("view-1"))

    # print(manager.create_job("job-name2"))

    # print(manager.get_job_info("job-name2"))
    # print(manager.get_job_config("job-name2"))
    print(manager.reconfig_job("job-name2"))

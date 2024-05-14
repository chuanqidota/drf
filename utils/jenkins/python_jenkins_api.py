"""
    python-jenkins==1.8.2
"""
"""
<project> - 作业的根元素。
<name> - 作业的名称。
<description> - 作业的描述。
<url> - 作业的 URL。
<actions> - 包含作业的元数据，如参数、构建触发器等。
<builders> - 存储构建步骤，例如执行 Shell 命令、Maven 目标、Gradle 任务等。
<publishers> - 包含构建后的行为，如邮件通知、归档工件等。
<buildWrappers> - 作业构建时的环境配置，如环境变量、SSH 凭证等。
<scm> - 源代码管理配置，如 Git、Subversion 等。
<triggers> - 构建触发器，如定时构建、代码仓库 webhook 等。
<properties> - 作业的属性，可能包括参数化构建、矩阵配置等。
<parameters> - 参数化构建的参数定义。
<parameterDefinitions> - 参数列表，每个参数是一个 <hudson.model.StringParameterDefinition> 或其他类型。
<definition> - 表示构建流程，对于 Pipeline 作业，通常包含一个 <jenkins.plugins.pipeline.PipelineScript> 元素，其中包含 Pipeline 脚本的文本

<project>
  <actions/>
  <description>Example Pipeline Job</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>MESSAGE</name>
          <description>Message to display</description>
          <defaultValue>Hello, World!</defaultValue>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition>
    <jenkins.plugins.pipeline.PipelineScript>
      <script>
        pipeline {
          agent any
          stages {
            stage('Example') {
              steps {
                echo "${params.MESSAGE}"
              }
            }
          }
        }
      </script>
      <isInheriting>true</isInheriting>
    </jenkins.plugins.pipeline.PipelineScript>
  </definition>
  ...
</project>

"""
from xml.etree import ElementTree

import jenkins


class JenkinsManager:
    def __init__(self, url, username, password):
        self.jenkins = jenkins.Jenkins(url, username=username, password=password)

    def create_view(self, view_name, xml=jenkins.EMPTY_VIEW_CONFIG_XML):
        self.jenkins.create_view(view_name, xml)

    def get_view_config(self, view_name):
        """

        :param view_name:
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

        :return:
            [{'_class': 'hudson.model.AllView', 'name': 'all', 'url': 'http://localhost:8080/'}, {'_class': 'hudson.model.ListView', 'name': 'view-1', 'url': 'http://localhost:8080/view/view-1/'}]
        """
        return self.jenkins.get_views()

    def delete_view(self, view_name):
        self.jenkins.delete_view(view_name)

    def get_view_jobs(self, view_name):
        """获取Jenkins视图中的作业列表"""
        return self.jenkins.get_jobs(view_name=view_name)

    def create_job(self, job_name, xml=jenkins.EMPTY_CONFIG_XML):
        self.jenkins.create_job(job_name, xml)

    def get_all_jobs(self):
        return self.jenkins.get_all_jobs()

    def get_job_info(self, job_name):
        """
            {'_class': 'hudson.model.FreeStyleProject', 'actions': [{}, {}, {}, {}, {'_class': 'org.jenkinsci.plugins.displayurlapi.actions.JobDisplayAction'}, {'_class': 'com.cloudbees.plugins.credentials.ViewCredentialsAction'}], 'description': None, 'displayName': 'job-name2', 'displayNameOrNull': None, 'fullDisplayName': 'job-name2', 'fullName': 'job-name2', 'name': 'job-name2', 'url': 'http://localhost:8080/job/job-name2/', 'buildable': True, 'builds': [], 'color': 'notbuilt', 'firstBuild': None, 'healthReport': [], 'inQueue': False, 'keepDependencies': False, 'lastBuild': None, 'lastCompletedBuild': None, 'lastFailedBuild': None, 'lastStableBuild': None, 'lastSuccessfulBuild': None, 'lastUnstableBuild': None, 'lastUnsuccessfulBuild': None, 'nextBuildNumber': 1, 'property': [], 'queueItem': None, 'concurrentBuild': False, 'disabled': False, 'downstreamProjects': [], 'labelExpression': None, 'scm': {'_class': 'hudson.scm.NullSCM'}, 'upstreamProjects': []}
        :param job_name:
        :return:
        """
        return self.jenkins.get_job_info(job_name)

    def get_job_config(self, job_name):
        """

        :param job_name:
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
        self.jenkins.reconfig_job(job_name, xml)

    def job_exists(self, job_name):
        return self.jenkins.job_exists(job_name)

    def disable_job(self, job_name):
        return self.jenkins.disable_job(job_name)

    def enable_job(self, job_name):
        return self.jenkins.enable_job(job_name)

    def delete_job(self, job_name):
        return self.jenkins.delete_job(job_name)

    def build_job(self, job_name, parameters=None):
        return self.jenkins.build_job(job_name, parameters)

    def stop_build(self, job_name, number):
        return self.jenkins.stop_build(job_name, number)

    def delete_build(self, job_name, number):
        return self.jenkins.delete_build(job_name, number)

    def get_running_builds(self):
        return self.jenkins.get_running_builds()

    def get_last_build_info(self, job_name):
        job_info = self.get_job_info(job_name)
        return self.get_build_info(job_name, job_info['lastBuild']['number'])

    def set_next_build_number(self, job_name, number):
        return self.jenkins.set_next_build_number(job_name, number)

    def get_build_info(self, job_name, build_number):
        return self.jenkins.get_build_info(job_name, build_number)

    def check_jenkinsfile_syntax(self, jenkinsfile):
        return self.jenkins.check_jenkinsfile_syntax(jenkinsfile)

    @staticmethod
    def _parse_xml_root_str(config_xml):
        xml_root = ElementTree.fromstring(config_xml)
        return xml_root

    @staticmethod
    def _parse_xml_root_file(config_xml):
        with open(config_xml, 'r') as f:
            xml_root = ElementTree.XML(f.read())
        return xml_root

    def replace_xml(self, job_name, xml_root, **kwargs):
        """

        :param job_name:
        :param xml_root:
        :param kwargs:
        :return:
        """
        # 更改方法
        # root.find("").text = kwargs.get("")
        updated_config_xml = ElementTree.tostring(xml_root, encoding="utf-8").decode("utf-8")
        self.jenkins.reconfig_job(job_name, updated_config_xml)

    


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

# -*- coding: utf-8 -*-
import os
import inspect
import traceback

from flask import current_app, g
from gitlab import const
from gitlab.exceptions import GitlabCreateError

from app.lib.es import write_order_log_kafka
from app.service import CMDBService
from app.extension import activiti
from app.service.activiti import ActivitiService
from app.service.autoconf import AutoconfService
from app.service.domain import DomainService, NewDomainHandle
from app.service.scaffold import ScaffoldService
from app.service.gitlab import GitLabService
from app.service.helper import (
    get_project_path,
    get_ci_id,
    get_approval_info
)
from app.service.mysql_service import MySQlService
from app.lib.decorator import update_process
from app.lib.notice_email import Email
from app.model.wf_order import WFOrder
from app.task.tasks import (
    task_approval_notice,
    task_complete_notice,
    task_delivery_notice,
    task_create_ci,
    task_generate_maven_project,
    WORKFLOW_CENTER_QUEUE
)
from app.lib.consts import (
    Xmx,
    MaxPermSize,
    CORE_MAPPING,
    MEMORY_MAPPING,
    ENV_DOMAIN_MAPPING,
    JAVA_OPTIONS_MAPPING
)


class ProcessAppApplication(object):
    """
    应用申请流程, activiti process identifier: ProcessAppApplication
    http://workflow.itcjf.com/activiti-app/editor/#/processes/6d674d22-4ed5-49b6-b76f-718f3c62fa45
    """

    def task_submit_form(self, *args, **kwargs):
        """
        应用申请-提交表单任务
        :param args:
        :param kwargs:
        :return:
        """
        # 提交表单, 指定申请人leader审批并发送通知
        # 当前运行函数名
        func_name = inspect.stack()[0][3]
        task_id = ActivitiService.get_task_by_process_instance_id(kwargs.get('process_id'), func_name)

        # 查询审批人
        employees = get_approval_info(
            kwargs.get('business'),
            kwargs.get('project'),
        )
        assignees = [emp.get('ad_account') for emp in employees]

        # 完成当前task
        variables = {'assigneeList': assignees}
        activiti.api.task_actions(task_id, 'complete', variables=variables)

        # 审批通知
        order_no = kwargs.get('order_no')
        task_approval_notice.apply_async(args=[order_no, assignees], queue=WORKFLOW_CENTER_QUEUE)

    @update_process
    def task_applicant_leader_audit(self, *args, **kwargs):
        """
        应用申请-申请人leader审批任务
        :param args:
        :param kwargs:
        :return:
        """
        # 完成当前task
        task_id = kwargs.get('task_id')
        order_no = kwargs.get('order_no')
        _pass = kwargs.get('pass')
        # activiti.api.task_actions(task_id, 'complete', variables={'pass': _pass})
        variables = {'pass': _pass}

        if _pass:
            # DB资源, 是否需要MySQL或Redis, 需要任一数据库但情况下需要DBA先检查
            require_mysql = kwargs.get('requireMysql')
            require_redis = kwargs.get('requireRedis')
            if require_mysql or require_redis:
                # 需要DBA, Activiti网关变量 ${require_dba==1}
                variables['require_dba'] = 1
                # 通知DBA
                roles = ['DBA']
            else:
                # 不需要DBA, Activiti网关变量 ${require_dba==0}
                variables['require_dba'] = 0
                # 通知SOR
                roles = ['SOR']
            # 业务线负责人同意, 通知DBA或SOR处理
            task_delivery_notice.apply_async(args=[order_no, roles], queue=WORKFLOW_CENTER_QUEUE)
        else:
            # 流程工单更新
            order = WFOrder.get_or_404(id=kwargs.get('order_id'))
            order.update(commit=True, **{'status': 'STATE_INITIAL'})

        activiti.api.task_actions(task_id, 'complete', variables=variables)

    @update_process
    def task_dba_handle(self, *args, **kwargs):
        """
        应用申请-DBA处理任务
        :param args:
        :param kwargs:
        :return:
        """
        # 完成当前task
        task_id = kwargs.get('task_id')
        order_no = kwargs.get('order_no')
        _pass = kwargs.get('pass')
        activiti.api.task_actions(task_id, 'complete', variables={'pass': _pass})

        if _pass:
            task_delivery_notice.apply_async(args=[order_no, ['SOR']], queue=WORKFLOW_CENTER_QUEUE)
        else:
            # 查询CMDB
            bg_ci_id = kwargs.get('business')  # 业务线ci
            # 查询业务线负责人
            emp = CMDBService.get_bg_head(bg_ci_id)
            assignee = emp.get('EmailPrefix')

            # 查询/认领task
            process_id = kwargs.get('process_id')
            task_id = ActivitiService.get_task_by_process_instance_id(process_id)
            activiti.api.task_actions(task_id, 'claim', assignee=assignee)

            # 通知业务线负责人处理
            task_approval_notice.apply_async(args=[order_no, [assignee]], queue=WORKFLOW_CENTER_QUEUE)

    @update_process
    def task_sor_handle(self, *args, **kwargs):
        """
        应用申请-SOR处理任务
        :param args:
        :param kwargs:
        :return:
        """
        # 审批,拒绝回到修改申请表单任务,同意进入目标业务线负责人审批任务
        task_id = kwargs.get('task_id')
        order_no = kwargs.get('order_no')
        _pass = kwargs.get('pass')

        # 完成当前task
        activiti.api.task_actions(task_id, 'complete', variables={'pass': _pass})

        # SOR驳回
        if _pass:
            # SOR同意
            # 更新CMDB资源
            try:
                write_order_log_kafka(kwargs.get("order_no"), f"新应用申请-请求的全部参数-{kwargs}")
                write_order_log_kafka(kwargs.get("order_no"), f"影响环境-{kwargs.get('envs')}")
                write_order_log_kafka(kwargs.get("order_no"), f"查询cmdb-判断app是否存在:{kwargs.get('appCode')}")
                app_id = self.check_app_exist(*args, **kwargs)
                if app_id:
                    write_order_log_kafka(kwargs.get("order_no"),
                                          f"查询cmdb-判断app:{kwargs.get('appCode')}是否存在:存在")
                else:
                    write_order_log_kafka(kwargs.get("order_no"),
                                          f"查询cmdb-判断app:{kwargs.get('appCode')}是否存在:不存在")
                kwargs.update({"app_id": app_id})

                write_order_log_kafka(kwargs.get("order_no"), "更新cmdb-开始")
                self.task_cmdb_upgrade(*args, **kwargs)
                write_order_log_kafka(kwargs.get("order_no"), "更新cmdb-结束")

                # 更新GitLab资源
                write_order_log_kafka(kwargs.get("order_no"), "操作gitlab-开始")
                self.task_gitlab_upgrade(*args, **kwargs)
                write_order_log_kafka(kwargs.get("order_no"), "操作gitlab-结束")

                # 更新Autoconf资源
                write_order_log_kafka(kwargs.get("order_no"), "操作autoconf-开始")
                self.task_autoconf_upgrade(*args, **kwargs)
                write_order_log_kafka(kwargs.get("order_no"), "操作autoconf-结束")

                # 'JF-Web'|'JF-SWeb' 域名处理
                app_type = kwargs.get('appType')  # type:str
                if app_type in ('JF-Web', 'JF-SWeb'):
                    kwargs.update({
                        'appId': get_ci_id('App', 'AppCode', kwargs.get('appCode'))
                    })

                    # 老的
                    # DomainService.set_domain_record(*args, **kwargs)

                    # 若 CMDB K8Sconf异步创建, 处理域名时, 可能还没创建成功, 会存在异常
                    write_order_log_kafka(kwargs.get("order_no"), "操作域名-开始")
                    # 新的
                    if not kwargs.get('params', {}).get('domainParams', {}):
                        write_order_log_kafka(kwargs.get("order_no"), "操作域名-没有域名相关参数(域名已存在)-不处理")
                    else:
                        NewDomainHandle().handle(**kwargs)
                    write_order_log_kafka(kwargs.get("order_no"), "操作域名-结束")

                    # 邮件通知
                    # DomainName
                    domain_ci_id = kwargs.get('domainId')
                    domain_ci = CMDBService.get_by_ci_id(domain_ci_id).get('ci', {})  # type:dict
                    network_type = domain_ci.get('networkType', '')  # type:str
                    # "networkType": "innerNet"
                    if network_type == "innerNet":
                        # 查询CMDB
                        bg_ci_id = kwargs.get('business')  # 业务线ci
                        # 查询业务线负责人
                        emp = CMDBService.get_bg_head(bg_ci_id)
                        fullname = emp.get('FullName')

                        title = '新应用申请内部域名'
                        # to = 'dazhen.wang@ly.com'
                        to = 'tcjf-puprd@ly.com'
                        params = {
                            '': '存在新应用申请内部域名，烦请沟通确认是否接入统一认证。',
                            '新应用名称': kwargs.get('appCode'),
                            '应用负责人': fullname,
                        }
                        content = Email.get_rich_text_content(params)
                        Email.send_rich_text_email(title, to, content)
            except Exception as e:
                write_order_log_kafka(kwargs.get("order_no"), f"异常-{traceback.format_exc()}")
                raise e
        else:
            # 查询CMDB
            bg_ci_id = kwargs.get('business')  # 业务线ci
            # 查询业务线负责人
            emp = CMDBService.get_bg_head(bg_ci_id)
            assignee = emp.get('EmailPrefix')

            # 查询/认领task
            process_id = kwargs.get('process_id')
            task_id = ActivitiService.get_task_by_process_instance_id(process_id)
            activiti.api.task_actions(task_id, 'claim', assignee=assignee)

            # 通知业务线负责人处理
            task_approval_notice.apply_async(args=[order_no, [assignee]], queue=WORKFLOW_CENTER_QUEUE)
        write_order_log_kafka(kwargs.get("order_no"), "整体操作-完结")

    @update_process
    def task_cmdb_upgrade(self, *args, **kwargs):
        """
        应用申请-CMDB资源更新任务
        1 创建应用, 上级关联: 应用关联用户用户/业务线/项目组; 下级关联 部署节点|K8S配置/与数据库关系.
        2 部署类型: 容器(kubernetes), 创建K8sConf CI({appCode}_inte|prod|rc|stable), 部署方式值 K8s容器部署, 上级关联应用/环境/K8s集群;
        3 部署类型: 原方式(tradition), 创建K8sConf CI({appCode}_inte|prod|rc|stable), 部署方式值 原方式, 上级关联应用/环境, 创建部署节点上级关联应用/环境/服务器;

        CMDB创建"App"时, 新增属性 BaseImage
        创建AppCluster CI, AppCluster上级 应用, AppCluster下级 集群, 挂载点, Java参数
        :param args:
        :param kwargs:
        :return:
        """
        params = kwargs.get('params', {})  # type: dict
        """"
        {
        "hyperactivity":"否",
        "baseImage":"harbor.itcjf.com/base/javasrv:8u191",
        "k8sCluster":{
            "rc":{
                "k8sClusters":[
                    10014323,
                    10023140
                ]
            },
            "inte":{
                "k8sClusters":[
                    10013500
                ]
            },
            "prod":{
                "k8sClusters":[
                    10014323
                ]
            },
            "stable":{
                "k8sClusters":[
                    10010995
                ]
            }
        },
        "domainParams":{
            "rc":{
                "ssl":true,
                "toHttps":"是",
                "accessPath":"/",
                "resolution":10021939
            },
            "inte":{
                "ssl":true,
                "toHttps":"是",
                "accessPath":"/",
                "resolution":10021932
            },
            "prod":{
                "ssl":true,
                "toHttps":"是",
                "accessPath":"/",
                "resolution":10021940
            },
            "stable":{
                "ssl":true,
                "toHttps":"是",
                "accessPath":"/",
                "resolution":10017338
            }
        }
        }
        """

        # 新建应用CI 部署节点|K8S配置CI
        app_code = kwargs.get('appCode')
        app_level = kwargs.get('appLevel')
        app_type = kwargs.get('appType')
        remark = kwargs.get('remark')
        is_stable = kwargs.get('isStable')
        service_level = kwargs.get('serviceLevel')
        pkg_path = kwargs.get('pkgPath', '')
        comment = kwargs.get('comment', '')
        jenkins_url = kwargs.get('jenkinsUrl', '')
        sdk_version = kwargs.get('sdkVersion')
        git_url = kwargs.get('gitUrl', '')
        app_tech_stack = kwargs.get('appTechStack', '')
        app_params = {
            'AppCode': app_code,
            'AppLevel': app_level,
            'AppType': app_type,
            'Remark': remark,
            'LifeCycle': '申请中',
            'IsStable': '1' if is_stable else '0',
            'SupportParallellyIterate': '',
            'sdkVersion': sdk_version,
            'AppTechStack': app_tech_stack,
            'JenkinsBuildJavaVersion': sdk_version,  # jdk 1.8
            'ServiceLevel': service_level,
            'GitUrl': git_url,
            'PkgPath': pkg_path,
            'Comment': comment,
            'JenkinsUrl': jenkins_url,  # 可能有JenkinsUrl
            'HealthCheck': kwargs.get('healthCheck', ''),
            'Provider': kwargs.get('provider', ''),
            "BaseImage": params.get('baseImage', ''),
            "IfAlive": params.get('hyperactivity', '否'),  # 是否双活, "是", "否"
        }
        app_id = kwargs.get("app_id")
        if app_id:
            app_ci_id = app_id
            write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-应用已存在-不创建app")
        else:
            write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-应用不存在创建app参数:{app_params}")
            ar = CMDBService.create_ci(ci_type='App', **app_params)
            app_ci_id = ar.get('ci_id')

        # 上级关联 应用关联用户用户/业务线/项目组
        order = WFOrder.get_or_404(id=kwargs.get('order_id'))
        applicant = order.applicant_emp_name
        emp_ci_id = get_ci_id('Employee', 'EmailPrefix', applicant)
        business = kwargs.get('business')  # 业务线CI ID
        project = kwargs.get('project')  # 项目组CI ID
        write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-应用关联业务线-{business}")
        CMDBService.create_ci_first_relation(first_ci=business, second_ci=app_ci_id)
        write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-应用关联项目组-{project}")
        CMDBService.create_ci_first_relation(first_ci=project, second_ci=app_ci_id)
        write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-应用关联用户-{emp_ci_id}")
        CMDBService.create_ci_first_relation(first_ci=emp_ci_id, second_ci=app_ci_id)

        # 是否需要stable
        # is_stable = kwargs.get('isStable')  # type:bool
        # envs = list(CMDB_ENV_MAPPING.values())  # ['inte', 'stable', 'rc', 'prod']
        # effect_envs = current_app.config.get('EFFECT_ENVS')  # ['inte'] | ['inte', 'stable', 'rc', 'prod']
        envs = kwargs.get("envs")

        # 创建部署资源
        deploy_type = kwargs.get('deployType')  # "kubernetes"|"tradition"|"no"
        level_code = self._get_level_code(app_level)
        write_order_log_kafka(kwargs.get("order_no"), f"查询cmdb-部署类型-{deploy_type}-部署级别-{level_code}")

        # 查询CMDB是否已有K8sConf CI, 查询条件 K8sConfCode
        # K8sConfCode ${app_code}_${env}
        # conditions = {'K8sConfCode': f'*{app_code}*'}
        # cis = CMDBService.search(conditions, 'K8sConf').get('result')  # K8sConf cis
        # # 根据应用查询已有K8sConfCode
        # conf_codes = list(map(lambda v: v.get('K8sConfCode'), cis))

        # 容器部署/原方式部署均需要生成K8S配置
        k8s_confs = []

        # AppCluster CIS
        # app_cluster_cis = CMDBService.search({'AppClusterName': f'*{app_code}*'}, 'AppCluster').get('result', [])
        # app_cluster_names = list(map(lambda v: v.get('AppClusterName'), app_cluster_cis))
        # Docker部署需要生成AppCluster CIS
        app_clusters = []
        # "DeployType": "Docker",  # "Server", "Docker" 默认"Docker"
        if deploy_type == 'Docker':
            # baseImage, k8sCluster参数
            base_image = params.get('baseImage')
            k8s_cluster_params = params.get('k8sCluster', {})  # type: dict

            # MountPoint 关联同一个
            mount_point_ci_id = get_ci_id('MountPoint', 'MountName', "public")

            for env, k8s_clusters_map in k8s_cluster_params.items():
                write_order_log_kafka(kwargs.get("order_no"), f"查询cmdb-操作针对环境:{env}")
                # rc {'k8sClusters': [10014323, 10023140]}
                # inte {'k8sClusters': [10013500]}
                # prod {'k8sClusters': [10014323]}
                # stable {'k8sClusters': [10010995]}
                k8s_cluster_ci_ids = k8s_clusters_map.get('k8sClusters')  # type: list
                # ---- K8sConf ----
                k8s_conf_code = f'{app_code}_{env}'
                # K8sConf inte|stable|rc|prod 4条数据, 各环境只需关联一个K8SCluster
                replicas = self._get_replicas(level_code, env)
                k8s_conf = {
                    "BaseImage": base_image,
                    "CommunicateProtocol": None,
                    "ConfStatus": '待上线',
                    "DeployType": 'K8s容器部署',
                    "IsSkywalking": '2' if kwargs.get('isSkywalking') else '',
                    "IsXpro": '1' if kwargs.get('isXpro') else '',
                    "JvmParams": None,
                    "K8sConfCode": k8s_conf_code,
                    "MaxPermSize": MaxPermSize,
                    "NodePort": None,
                    "Replicas": replicas,
                    "Xmx": Xmx,
                    "DataAgent": "v1.0",
                    # "_id": 10006671,
                    # "_type": 78,
                    # "ci_type": "K8sConf",
                    # "unique": "K8sConfCode"
                }
                # 4 个环境关联的应用CI ID一样
                env_ci_id = get_ci_id('Environment', 'EnvironmentCode', env)
                k8s_confs.append(
                    {'k8s_conf': k8s_conf, 'env_ci_id': env_ci_id, 'k8s_cluster_ci_id': k8s_cluster_ci_ids[0]})
                # ---- K8sConf ----

                # ---- AppCluster ----
                # AppCluster inf-metadata-srv_inte_sztcyl, inte|stable|rc|prod, 5条数据, prod可能2条各环境只需关联一个K8SCluster
                # 按照应用名称搜索现有的AppCluster, AppClusterName={App.AppCode}_{Environment.EnvironmentCode}_{IDC.IDCAbbr}
                # AppClusterName示例: "inf-metadata-srv_inte_sztcyl"
                # CheckPath
                if app_type in ("JF-Srv", "JF-SWeb"):
                    check_path = "/health"
                elif app_type == 'JF-Web':
                    check_path = "/nohup.html"
                else:
                    check_path = "/health"

                # DomainName
                if app_type in ('JF-Web', 'JF-SWeb'):
                    domain_ci_id = kwargs.get('domainId')
                    domain_ci = CMDBService.get_by_ci_id(domain_ci_id).get('ci', {})  # type:dict
                    domain_name = domain_ci.get('DomainName')  # type:str
                    domain_version = domain_ci.get('DomainVersion')  # type:str
                    subdomain = kwargs.get('subdomain')
                    domain_params = kwargs.get('params', {}).get('domainParams', {})  # type: dict
                else:
                    subdomain = ''
                    domain_name = ''
                    domain_params = {}

                if app_type in ('JF-Web', 'JF-SWeb'):
                    rr = f'{subdomain}' + ENV_DOMAIN_MAPPING.get(env)
                    record_fullname = f'{rr}.{domain_name}'
                    access_path = domain_params.get(env, {}).get('accessPath', '/')
                    url_code = record_fullname if access_path == '/' else f"{record_fullname}_{access_path.lstrip('/').replace('/', '-')}"
                else:
                    url_code = ''

                for k8s_cluster_ci_id in k8s_cluster_ci_ids:
                    # IDC.IDCAbbr k8scluster上级机房
                    # K8SCluster上级IDC
                    r = CMDBService.get_firsts(k8s_cluster_ci_id) or {}
                    k8s_cluster_first_cis = r.get('first_cis', []) or []
                    idc_cis = list(filter(lambda arg: arg.get('ci_type') == 'IDC', k8s_cluster_first_cis))
                    idc_ci = idc_cis and idc_cis[0] or {}
                    idc_abbr = idc_ci.get('IDCAbbr', None)

                    app_cluster_name = f'{app_code}_{env}_{idc_abbr}'

                    app_cluster = {
                        "CheckTimeout": "5",
                        "FailureTimes": "3",
                        "SuccessTimes": "1",
                        "CheckPeriod": "60",
                        "CheckPath": check_path,
                        "InitialDelay": "90",
                        "HealthCheckCmd": "",
                        "HealthCheckType": "httpGet",
                        "AppClusterName": app_cluster_name,
                        "DataAgent": "v1.0",  # "" | "v1.0"
                        "IDCName": idc_abbr,  # szth|wxyd
                        "Env": env,  # "inte","rc","prod", "stable"
                        "NodePort": "",
                        "CommunicateProtocol": "HTTP",  # "HTTP", "TCP", "UDP"  默认"HTTP"
                        # "DeployType": kwargs.get('deployType', 'Docker'),  # "Server", "Docker" 默认"Docker"
                        "DeployType": deploy_type,  # "Server", "Docker" 默认"Docker"
                        "IsSkywalking": '2' if kwargs.get('isSkywalking') else '',
                        "Replicas": replicas,
                        "MaxPermSize": MaxPermSize,
                        "Xmx": Xmx,
                        "Port": "8080",
                        "Core": CORE_MAPPING.get(env),
                        "Memory": MEMORY_MAPPING.get(env),
                        "ConfStatus": "待上线",
                        # "UrlCode": '',  # 多个逗号分割
                        "UrlCode": url_code
                    }

                    # JavaOptions 新建JavaOptions取CI ID
                    common_param = JAVA_OPTIONS_MAPPING.get('common_param', {}).get(app_type)
                    sdk_version_param = JAVA_OPTIONS_MAPPING.get('sdk_version_param', {}).get(sdk_version)
                    extra_version_param = JAVA_OPTIONS_MAPPING.get('extra_version_param', {}).get(env)
                    p_jvm_params = f'{common_param} {sdk_version_param} {extra_version_param}'
                    t_jvm_params = p_jvm_params.split(" ")
                    std_arg = [s for s in t_jvm_params if s.startswith('-') and not s.startswith(('-X', '-XX', '-D'))]
                    unstd_arg = [s for s in t_jvm_params if s.startswith('-X') and not s.startswith('-XX')]
                    unstable = [s for s in t_jvm_params if s.startswith('-XX')]
                    sysarg = [s for s in t_jvm_params if s.startswith('-D')]

                    java_options_params = {
                        "AppCode": app_cluster_name,
                        "Stdarg": " ".join(std_arg),
                        "Unstdarg": " ".join(unstd_arg),
                        "Unstable": " ".join(unstable),
                        "Sysarg": " ".join(sysarg),
                    }
                    write_order_log_kafka(kwargs.get("order_no"),
                                          f"更新cmdb-环境:{env};创建java参数-{java_options_params}")
                    cr = CMDBService.create_ci(ci_type='JavaOptions', **java_options_params)
                    java_options_ci_id = cr.get('ci_id')

                    # MountPoint CI ID, 当前MountPoint仅一个实例
                    # mount_point_ci_id = get_ci_id('MountPoint', 'MountName', "public")

                    app_clusters.append({
                        'app_cluster': app_cluster,
                        'app_ci_id': app_ci_id,
                        'k8s_cluster_ci_id': k8s_cluster_ci_id,
                        'java_options_ci_id': java_options_ci_id,
                        'mount_point_ci_id': mount_point_ci_id,
                    })
                # ---- AppCluster ----
        elif deploy_type == 'Server':
            nodes = []
            # for env in effect_envs:
            for env in envs:
                k8s_conf_code = f'{app_code}_{env}'

                k8s_conf = {
                    # "BaseImage": None,
                    # "CommunicateProtocol": None,
                    "ConfStatus": '待上线',
                    "DeployType": '原方式',
                    # "IsSkywalking": None,
                    # "IsXpro": None,
                    # "JvmParams": None,
                    "K8sConfCode": k8s_conf_code,
                    # "MaxPermSize": None,
                    # "NodePort": None,
                    # "Replicas": None,
                    # "Xmx": None,
                    # "_id": 10006671,
                    # "_type": 78,
                    # "ci_type": "K8sConf",
                    # "unique": "K8sConfCode"
                }
                env_ci_id = get_ci_id('Environment', 'EnvironmentCode', env)
                k8s_confs.append({'k8s_conf': k8s_conf, 'env_ci_id': env_ci_id, 'k8s_cluster_ci_id': None})

                # 2022/10/10 11:50与SOR(qingwen.zhang)确认,原方式部署CMDB生成部署节点/K8S配置CI(仅部署方式值(原方式)有用)
                # 原方式部署,部署节点(AppDeployNode)CI
                ips = params.get('node', {}).get(env, [])
                for ip in ips:
                    node_code = f'{ip}_{app_code}_1'
                    node = {
                        "AppDeployNodeCode": node_code,
                        "AppDeployNodeDesc": node_code,
                        # "JavaAgent": '',
                        "MaxPermSize": MaxPermSize,
                        "NodeAlias": None,
                        "NodeID": "1",
                        "NodeStatus": "待上线",
                        "Port": 8000,
                        "Xmx": Xmx,
                        "XproPort": '1' if kwargs.get('isXpro') else '',
                        # "_id": 10011498,
                        # "_type": 76,
                        # "ci_type": "AppDeployNode",
                        # "unique": "AppDeployNodeCode"
                    }
                    server_ci_id = get_ci_id('Server', 'ServerIP', ip)
                    nodes.append({'node': node, 'env_ci_id': env_ci_id, 'server_ci_id': server_ci_id})
            write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-创建部署节点(异步)-{nodes}")
            task_create_ci.apply_async(args=['AppDeployNode', app_ci_id, nodes], queue=WORKFLOW_CENTER_QUEUE)
        else:
            write_order_log_kafka(kwargs.get("order_no"), f"错误-部署方式不对-{deploy_type}")
            current_app.logger.info(f'{app_code} 部署方式 {deploy_type}')

        # celery异步生成AppCluster
        write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-创建应用集群及增加应用关联-{app_clusters}")
        task_create_ci("AppCluster", app_ci_id, app_clusters)
        # task_create_ci.apply_async(args=['AppCluster', app_ci_id, app_clusters], queue=WORKFLOW_CENTER_QUEUE)
        # task_create_ci.apply_async(args=['K8sConf', app_ci_id, k8s_confs], queue=WORKFLOW_CENTER_QUEUE)
        # 同步调用celery函数
        write_order_log_kafka(kwargs.get("order_no"), f"更新cmdb-创建k8s配置-{k8s_confs}")
        task_create_ci('K8sConf', app_ci_id, k8s_confs)

        # 完成当前task
        process_id = kwargs.get('process_id')
        task_id = ActivitiService.get_task_by_process_instance_id(process_id)
        activiti.api.task_actions(task_id, 'complete')

    def check_app_exist(self, *args, **kwargs):
        app_code = kwargs.get('appCode')
        exist_apps = CMDBService.search({"AppCode": app_code}, "App").get("result")
        if exist_apps:
            return exist_apps[0].get('_id')
        else:
            return None

    @update_process
    def task_gitlab_upgrade(self, *args, **kwargs):
        """
        ['JF-Jetty', 'JF-Web', 'JF-Srv', 'JF-Ui', 'JF-Jar', 'JF-SWeb', 'JF-Component']
        应用申请-GitLab资源更新任务
        :param args:
        :param kwargs:
        :return:
        """
        if kwargs.get("app_id"):
            write_order_log_kafka(kwargs.get("order_no"), f"操作gitlab-应用已存在-不操作gitlab")
            process_id = kwargs.get('process_id')
            task_id = ActivitiService.get_task_by_process_instance_id(process_id)
            activiti.api.task_actions(task_id, 'complete')
            return

        # GitLab区分新建仓库|关联仓库|不需要 "create"|"correlation"|"no"
        gitlab_requirement = kwargs.get('gitRequirement')
        write_order_log_kafka(kwargs.get("order_no"), f"操作gitlab-动作-{gitlab_requirement}")
        if gitlab_requirement == 'create':
            # 新建GitLab库
            r = CMDBService.get_by_ci_id(kwargs.get('project'))
            # 项目组CI GitNameSpace
            ns_url = r.get('ci', {}).get('GitNameSpace')
            # GitLab group内新建project
            visibility = kwargs.get('gitVisibility', 'private') or 'private'
            description = str(kwargs.get("remark", ""))
            write_order_log_kafka(kwargs.get("order_no"),
                                  f"操作gitlab-创建项目-组:{ns_url};项目:{kwargs.get('appCode')}")
            project = GitLabService.create_project_in_group(ns_url, kwargs.get('appCode'), visibility, description)

            # master 写 readme
            project_path = get_project_path()
            readme_file_path = os.path.join(project_path, 'templates', 'README.txt')
            write_order_log_kafka(kwargs.get("order_no"), f"操作gitlab-提交-README.md")
            readme_commit_id = GitLabService.create_new_commit_in_project(
                project_id=project.id,
                git_new_file_path='README.md',
                local_file=readme_file_path)
            if not readme_commit_id:
                raise ValueError('操作gitlab-创建readme失败')

            # java项目脚手架
            app_type = kwargs.get('appType')  # type:str
            app_tech_stack = kwargs.get('appTechStack', 'Java')  # type: str
            _types = kwargs.get('orderType')  # type:list
            # 仅支持java 'sweb', 'srv'
            if 'Java' in app_tech_stack and app_type in ('JF-Srv', 'JF-SWeb'):
                """
                mysql_path, redis_path, mqs_enable = None, None, None
                # eg: '/db/mysql/inf/biz_common_db'
                # 仅新建库时, mvn生成的项目传mysqlPath
                if kwargs.get('requireMysql', False) and 'create' in _types:
                    db_bu_ci_id = kwargs.get('DbBu')  # DB业务线CI ID
                    mysql_schema = kwargs.get('mysqlSchema')  # 新建mysql库名, eg:tcbiz_ins_bgw_fql
                    mysql_bg = CMDBService.get_by_ci_id(db_bu_ci_id)  # type:dict
                    mysql_bg_abbr = mysql_bg.get('ci', {}).get('DBBuAbbr')
                    mysql_path = AutoconfService.get_config_key(mysql_bg_abbr.lower(), mysql_schema)
                # eg: '/redis/inf'
                if kwargs.get('requireRedis', False):
                    redis_config_keys = kwargs.get('redisConfigKeys')
                    redis_path = redis_config_keys[0]
                # mqs_enable True ｜ False
                。
                if kwargs.get('requireRocketmq', False):
                    mqs_enable = True
                # 生成zip
                ScaffoldService.generate_java_project(kwargs.get('appCode'), mysql_path, redis_path, mqs_enable)
                # 提交文件
                ScaffoldService.commit_java_project_file(project, kwargs.get('appCode'))
                """
                # # 仅新建库时, mvn生成项目
                # # 生成zip
                order = WFOrder.get_or_404(id=kwargs.get('order_id'))
                # # applicant_emp_code applicant_emp_name
                # ScaffoldService.generate_maven_project(order.applicant_emp_code, *args, **kwargs)
                # # 提交文件
                # ScaffoldService.commit_java_project_file(project, kwargs.get('appCode'))
                write_order_log_kafka(kwargs.get("order_no"), f"操作gitlab-执行mvn命令生成项目")
                task_generate_maven_project.apply_async(args=[project.id, order.applicant_emp_code, kwargs],
                                                        queue=WORKFLOW_CENTER_QUEUE)
            else:
                write_order_log_kafka(kwargs.get("order_no"),
                                      f"操作gitlab-创建release分支,设默认分支release,设置保护分支")
                ScaffoldService.set_branches(project.id)
            # # 创建release分支
            # GitLabService.create_branch_in_project(project=project, branch_name='release')
            #
            # # enable_deploy_keys
            # GitLabService.enable_deploy_keys(project)
            #
            # # 设定默认branch为release
            # GitLabService.set_default_branch(project, 'release')
            #
            # # 查询project的protectedbranches
            # p_branches = project.protectedbranches.list()
            # # 可能是[] | ['master'] | ['release'] | ['master', 'release']
            # p_branch_names = [p_branch.name for p_branch in p_branches]
            # current_app.logger.info(f'保护分支, {p_branch_names}')
            #
            # # 'release' 保护分支可能已存在, 偶现.
            # # 设定保护分支策略，参考需求：http://10.100.172.177/issues/80054
            # # 'master' 'release' 保护分支可能已存在, 偶现.
            # if 'master' not in p_branch_names:
            #     GitLabService.set_protected_branches(project, 'master', const.AccessLevel.MAINTAINER,
            #                                          const.AccessLevel.MAINTAINER)
            # if 'release' not in p_branch_names:
            #     try:
            #         GitLabService.set_protected_branches(project, 'release', const.AccessLevel.DEVELOPER,
            #                                              const.AccessLevel.MAINTAINER)
            #     except GitlabCreateError as e:
            #         current_app.logger.error(f"创建保护分支 'release' 失败, {e.response_code}, {e.error_message}")
            # git_url
            ssh_url_to_repo = project.ssh_url_to_repo
            git_url = ssh_url_to_repo
        elif gitlab_requirement == 'correlation':
            git_url = kwargs.get('gitUrl')
        elif gitlab_requirement == 'no':
            git_url = None
        else:
            git_url = None

        # 更新状态 GitUrl
        app_code = kwargs.get('appCode')
        # search CMDB
        app_ci_id = get_ci_id('App', 'AppCode', app_code)

        # 更新CMDB GitUrl
        if git_url:
            write_order_log_kafka(kwargs.get("order_no"), f"操作gitlab-更新cmdb-应用的giturl-{git_url}")
            CMDBService.update_by_ci_id(app_ci_id, 'App', **{'GitUrl': git_url})

        # 完成当前task
        process_id = kwargs.get('process_id')
        task_id = ActivitiService.get_task_by_process_instance_id(process_id)
        activiti.api.task_actions(task_id, 'complete')

    @update_process
    def task_autoconf_upgrade(self, *args, **kwargs):
        """
        应用申请-配置中心资源创建
        :param args:
        :param kwargs:
        :return:
        """
        # 配置中心是否需要新建应用, requireAutoconf true|false
        require_autoconf = kwargs.get('requireAutoconf')
        write_order_log_kafka(kwargs.get("order_no"), f"操作autoconf-是否需要操作-{require_autoconf}")
        if require_autoconf:
            # 此步骤配置中心创建应用,此时不关联配置
            # autoconf_envs = current_app.config.get('AUTOCONF_ENVS')
            envs = kwargs.get("envs")

            # 仅不存在应用的环境创建应用
            app_code = kwargs.get('appCode')
            business_id = kwargs.get('business')
            write_order_log_kafka(kwargs.get("order_no"),
                                  f"操作autoconf-查询应用-环境:{envs};应用:{app_code};业务线确定autoconf:{business_id}")
            app_nil_map = AutoconfService.get_app(envs, app_code, business_id=business_id)
            app_nil_msgs = []
            app_nil_envs = []  # 应用不存在or非激活的env列表
            for env, nil in app_nil_map.items():
                if nil:
                    app_nil_envs.append(env)
                    app_nil_msgs.append(f'{app_code}在{env}不存在.')
            write_order_log_kafka(kwargs.get("order_no"),
                                  f"操作autoconf-查询应用在该环境中不存在:{app_nil_envs}")
            current_app.logger.info(f'应用检测: {app_nil_msgs}')
            # kwargs.get('project') 项目组CI ID
            r = CMDBService.get_by_ci_id(kwargs.get('project'))
            # 项目组CI InfBuName 对应配置心 组
            inf_bu_name = r.get('ci', {}).get('InfBuName')

            # 仅存在group的环境注册应用
            write_order_log_kafka(kwargs.get("order_no"),
                                  f"操作autoconf-查询分组-环境:{envs};组名:{inf_bu_name};业务线确定autoconf:{business_id}")
            groups_map = AutoconfService.search_group(envs, inf_bu_name, business_id=business_id)  # type:dict
            group_exist_envs = []
            for env, group in groups_map.items():
                if group:
                    group_exist_envs.append(env)
            write_order_log_kafka(kwargs.get("order_no"), f"操作autoconf-查询组在该环境中存在:{group_exist_envs}")
            # 应用不存在&组存在的环境注册应用
            _envs = list(set(app_nil_envs) & set(group_exist_envs))
            if _envs:
                write_order_log_kafka(kwargs.get("order_no"),
                                      f"操作autoconf-应用不存在and组存在的环境:{_envs}-注册应用")
                write_order_log_kafka(kwargs.get("order_no"),
                                      f"操作autoconf-注册应用-环境:{_envs};组:{inf_bu_name};应用:{app_code}")
                AutoconfService.register_app(_envs, app_code, inf_bu_name, business_id=business_id)
            else:
                write_order_log_kafka(kwargs.get("order_no"),
                                      f"操作autoconf-应用不存在and组存在的环境:{_envs}-环境不存在-无法注册应用")

            # zk kafka ldap xxl-job mq 配置key关联到应用
            config_keys = kwargs.get('configKeys', [])

            #
            # zookeeper: middleware_public_zk(默认只能选这个)
            #
            # zookeeper: middleware_inf_zk（允许架构选择）
            #
            # kafka: middleware_public_kafka
            #
            # ldap: middleware_public_ldap
            #
            # rocketmq: middleware_public_rocketmq
            #
            # xxl-job：inf-xxl-job
            if config_keys:
                write_order_log_kafka(kwargs.get("order_no"),
                                      f"操作autoconf-应用关联key-环境:{envs};应用:{app_code};key:{config_keys};业务线确定autoconf:{business_id}")
                AutoconfService.add_relevance(kwargs.get('order_id'), app_code, envs, config_keys,
                                              business_id=business_id)

        # 完成当前task,包容网关变量
        variables = {'require_mysql': 0, 'require_redis': 0, 'require_null': 1}

        # DB资源
        require_mysql = kwargs.get('requireMysql')
        require_redis = kwargs.get('requireRedis')

        # Redis/MySQL 需要任意一个资源,都不应直接结束流程,需要进入对应task
        if require_mysql:
            variables['require_mysql'] = 1
            variables['require_null'] = 0

        if require_redis:
            variables['require_redis'] = 1
            variables['require_null'] = 0

        # 提交task_autoconf_upgrade
        process_id = kwargs.get('process_id')
        task_id = ActivitiService.get_task_by_process_instance_id(process_id)
        activiti.api.task_actions(task_id, 'complete', variables=variables)

        write_order_log_kafka(kwargs.get("order_no"),
                              f"操作autoconf-mysql关联:{require_mysql};redis关联:{require_redis}")
        # 执行后续task
        if require_mysql:
            write_order_log_kafka(kwargs.get("order_no"), f"操作autoconf-mysql关联-开始")
            self.task_mysql_relation(*args, **kwargs)
            write_order_log_kafka(kwargs.get("order_no"), f"操作autoconf-mysql关联-结束")
        if require_redis:
            write_order_log_kafka(kwargs.get("order_no"), f"操作autoconf-redis关联-开始")
            self.task_redis_relation(*args, **kwargs)
            write_order_log_kafka(kwargs.get("order_no"), f"操作autoconf-redis关联-结束")

        if not require_mysql and not require_redis:
            write_order_log_kafka(kwargs.get("order_no"), f"操作autoconf-无需操作mysql关联和redis关联")
            # 更新工单
            order = WFOrder.get_or_404(id=kwargs.get('order_id'))
            order.update(commit=True, **{'status': 'STATE_COMPLETED'})

            # 通知
            order_no = kwargs.get('order_no')
            task_complete_notice.apply_async(args=[order_no], queue=WORKFLOW_CENTER_QUEUE)

    @update_process
    def task_mysql_relation(self, *args, **kwargs):
        """
        应用申请-mysql关联任务
        :param args:
        :param kwargs:
        :return:
        """
        # 当前运行函数名
        func_name = inspect.stack()[0][3]

        # mysql处理逻辑
        MySQlService.handler(*args, **kwargs)

        # 完成当前task
        task_id = ActivitiService.get_task_by_process_instance_id(kwargs.get('process_id'), func_name)
        activiti.api.task_actions(task_id, 'complete')

        # 更新工单
        order = WFOrder.get_or_404(id=kwargs.get('order_id'))
        order.update(commit=True, **{'status': 'STATE_COMPLETED'})

        # 通知
        order_no = kwargs.get('order_no')
        task_complete_notice.apply_async(args=[order_no], queue=WORKFLOW_CENTER_QUEUE)

    @update_process
    def task_redis_relation(self, *args, **kwargs):
        """
        应用申请-redis关联任务
        :param args:
        :param kwargs:
        :return:
        """
        # 当前运行函数名
        func_name = inspect.stack()[0][3]
        # CMDB维护redis配置key-业务线映射关系,新应用申请时前端自动根据业务线获取对应配置key并填充前端页面
        # redis关联逻辑
        order_id = kwargs.get('order_id')
        app_code = kwargs.get('appCode')
        redis_config_keys = kwargs.get('redisConfigKeys')
        # autoconf_envs = current_app.config.get('AUTOCONF_ENVS')
        envs = kwargs.get("envs")
        business_id = kwargs.get("business")
        write_order_log_kafka(kwargs.get("order_no"),
                              f"redis关联-环境:{envs};应用:{app_code};key:{redis_config_keys};业务线:{business_id}")
        AutoconfService.add_relevance(order_id, app_code, envs, redis_config_keys, business_id=business_id)

        # 完成当前task
        task_id = ActivitiService.get_task_by_process_instance_id(kwargs.get('process_id'), func_name)
        activiti.api.task_actions(task_id, 'complete')

        # 更新工单
        order = WFOrder.get_or_404(id=kwargs.get('order_id'))
        order.update(commit=True, **{'status': 'STATE_COMPLETED'})

        # 通知
        order_no = kwargs.get('order_no')
        task_complete_notice.apply_async(args=[order_no], queue=WORKFLOW_CENTER_QUEUE)

    @staticmethod
    def _rollback(*args, **kwargs):
        """
        应用申请-回滚资源-没用
        :param args:
        :param kwargs:
        :return:
        """
        # 参数
        app_code = kwargs.get('AppCode')
        # search CMDB
        conditions = {'AppCode': f'*{app_code}*'}
        response = CMDBService.search(conditions, 'App')

        app_ci_id = None
        git_url = None
        cis = response.get('result')
        for ci in cis:
            if ci.get('AppCode') == app_code:
                app_ci_id = ci.get('_id')
                git_url = ci.get('GitUrl')

        second_cis = CMDBService.get_all_second_cis(app_ci_id)

        second_cis_ids = []
        if second_cis and isinstance(second_cis, list):
            for ci in second_cis:
                if ci.get('ci_type') in ['K8sConf', 'AppDeployNode', 'DomainRecord']:
                    second_cis_ids.append(ci.get('_id'))

        # CMDB删除应用:删除上级关联 用户/业务线/项目组 删除下级关联 /K8S配置/部署节点/解析记录
        # 'K8sConf', 'AppDeployNode', 'DomainRecord'
        for second_cis_id in second_cis_ids:
            CMDBService.delete_ci_first_relation(first_ci=app_ci_id, second_ci=second_cis_id)
            CMDBService.del_by_ci_id(app_ci_id)
            CMDBService.del_by_ci_id(second_cis_id)

        # GitLab删除project
        GitLabService.del_project_by_repo_url(git_url)

        # Autoconf下线应用
        autoconf_envs = current_app.config.get('AUTOCONF_ENVS')
        # 检查是否已经下线,已经下线直接跳过
        business_id = kwargs.get("business")
        not_exist = AutoconfService.get_app(autoconf_envs, app_code, business_id=business_id)
        not_exist_msgs = []
        ne_envs = []  # 应用不存在or非激活的env列表
        for env, ne in not_exist.items():
            if ne:
                ne_envs.append(env)
                not_exist_msgs.append(f'{app_code} in {env} not exist.')

        # 删除应用不存在的env
        envs = list(set(autoconf_envs) - set(ne_envs))
        AutoconfService.deregister_app(envs, app_code, business_id=business_id)

        # 配置中心: mysql 只读引用/读写引用, redis关联应用在应用删除后会解除关联

    @classmethod
    def _get_memory_size(cls, mem_size):
        """
        获取内存对应的数字，单位M，默认512M
        :param mem_size: mem_size
        :return:
        """
        switcher = {
            '512M': 512,
            '1G': 1024,
            '2G': (1024 * 2),
            '4G': (1024 * 4),
            '8G': (1024 * 8),
        }
        return switcher.get(mem_size, 512)

    @staticmethod
    def _get_base_image(app_type, sdk_version):
        """
        获取base_image
        :param app_type: ["JF-Jetty","JF-Web","JF-Srv","JF-Ui","JF-Jar","JF-SWeb","JF-Component"]
        :param sdk_version: ["jdk1.8", "jdk1.7"]
        :return:
        """
        # note:目前仅支持Java技术栈
        if app_type == 'JF-Srv':
            # srv类型: srv_jdk1.8 / 'srv_jdk1.7'
            app_type_version = 'srv_jdk1.8'
            if '1.7' in sdk_version:
                app_type_version = 'srv_jdk1.7'
        elif app_type in ['JF-Web', 'JF-SWeb']:
            # web类型: web_tomcat8_jdk1.8 / web_tomcat7_jdk1.7
            app_type_version = 'web_tomcat8_jdk1.8'
            if '1.7' in sdk_version:
                app_type_version = 'web_tomcat7_jdk1.7'
        else:
            raise ValueError(f'查询app_type失败, {app_type}.')

        # BaseImage CIS
        response = CMDBService.search({'AppTypeVersion': f'*{app_type_version}*'}, 'BaseImage')
        cis = response.get('result')

        # base images
        images = []
        if len(cis) > 0:
            images = list(filter(lambda arg: arg.get('AppTypeVersion') == app_type_version, cis))

        image = images[0] if images else None

        if image:
            base_image = image.get('ImageUrl')
        else:
            raise ValueError(f'获取镜像失败, {response}.')

        return base_image

    @staticmethod
    def _get_replicas(level_code, env):
        """
        根据应用等级 环境查询副本数
        :param level_code:
        :param env:
        :return:
        """

        mapping = {
            "2": {"inte": 1, "rc": 1, "prod": 8, "stable": 1},  # "核心服务"
            "3": {"inte": 1, "rc": 1, "prod": 4, "stable": 1},  # "重要服务"
            "4": {"inte": 1, "rc": 1, "prod": 2, "stable": 1}  # "普通服务"
        }
        return mapping.get(level_code, {}).get(env, 1)

    @staticmethod
    def _get_level_code(level_name):
        """
        [
            {
                "AppLevelCode":"2",
                "AppLevelName":"核心服务",
                "_id":10001326,
                "_type":62,
                "ci_type":"AppLevel",
                "unique":"AppLevelCode"
            },
            {
                "AppLevelCode":"3",
                "AppLevelName":"重要服务",
                "_id":10001327,
                "_type":62,
                "ci_type":"AppLevel",
                "unique":"AppLevelCode"
            },
            {
                "AppLevelCode":"4",
                "AppLevelName":"普通服务",
                "_id":10001328,
                "_type":62,
                "ci_type":"AppLevel",
                "unique":"AppLevelCode"
            }
        ]

        :param level_name:
        :return:
        """
        response = CMDBService.search({'AppLevelName': f'*{level_name}*'}, 'AppLevel')
        cis = response.get('result')

        levels = []
        if len(cis) > 0:
            levels = list(filter(lambda arg: arg.get('AppLevelName') == level_name, cis))

        level = levels[0] if levels else None

        if level:
            level_code = level.get('AppLevelCode')
        else:
            raise ValueError(f'查询AppLevel失败, {response}.')

        return level_code

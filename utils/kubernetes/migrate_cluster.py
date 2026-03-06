# pip install kubernetes==29.0.0
import time
import traceback

from kubernetes import config, dynamic, client
from kubernetes.client import ApiClient, VersionApi, CoreV1Api, AppsV1Api, NetworkingV1Api
from kubernetes.dynamic import DynamicClient

CONFIG_SERVER2TOKEN = {

}


class InitK8sClient(object):
    """
        最基础的方式初始化客户端
    """

    @staticmethod
    def by_config_dict(config_dict: dict) -> ApiClient:
        """
            通过配置字段获取客户端
        :param config_dict: 配置字典
        :return:
        """
        assert not config_dict, "config_dict不能为空"
        client = config.new_client_from_config_dict(config_dict=config_dict)
        return client

    @staticmethod
    def by_token(api_server: str, token: str) -> ApiClient:
        """
            通过token初始化
        :param api_server: api-server
        :param token: token
        :return:
        """
        configuration = client.Configuration()
        configuration.host = api_server  # 替换为API地址
        configuration.verify_ssl = False  # 若使用自签名证书需关闭验证（生产环境不推荐）
        configuration.host = "https://{}".format(api_server)
        configuration.api_key = {"authorization": f"Bearer {token}"}
        client.Configuration.set_default(configuration)
        return client.ApiClient(configuration)

    @staticmethod
    def dynamic_by_config_dict(config_dict: dict) -> dynamic.DynamicClient:
        """
            通过配置获取动态客户端
        :param config_dict:
        :return:
        """
        client = config.new_client_from_config_dict(config_dict=config_dict)
        return dynamic.DynamicClient(client)

    @staticmethod
    def dynamic_by_token(api_server: str, token: str) -> dynamic.DynamicClient:
        """
            通过token初始化动态客户端
        :param api_server: api-server
        :param token: token
        :return:
        """
        assert not api_server, "api_server不能为空"
        assert not token, "token不能为空"
        configuration = client.Configuration()
        configuration.host = api_server  # 替换为API地址
        configuration.verify_ssl = False  # 若使用自签名证书需关闭验证（生产环境不推荐）
        configuration.api_key = {"authorization": f"Bearer {token}"}
        client.Configuration.set_default(configuration)
        return dynamic.DynamicClient(client)

    @staticmethod
    def dynamic_resources_api(dynamic_client: dynamic.DynamicClient,
                              api_version: str, kind: str) -> dynamic.ResourceList:
        """
            获取动态客户端操作的基础
        :param dynamic_client: 动态客户端
        :param api_version: 集群版本
        :param kind: 资源类型
        :return:
        """
        return dynamic_client.resources.get(api_version=api_version, kind=kind)


class HandleK8sSource(object):

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self.version_api = VersionApi(self.api_client)
        self.core_v1_api = CoreV1Api(self.api_client)
        self.apps_v1_api = AppsV1Api(self.api_client)
        self.net_v1_api = NetworkingV1Api(self.api_client)
        self.dynamic_api = DynamicClient(self.api_client)

    def get_version(self):
        """
            获取版本信息
        :return:
        """
        return self.version_api.get_code().git_version

    def get_namespace_names(self):
        """
            获取namespace信息
        :return:
        """
        namespaces = self.core_v1_api.list_namespace()
        return [i.metadata.name for i in namespaces.items]

    def get_deployment_names(self, namespace):
        """
            获取指定namespace下的dp的名称
        :param namespace:
        :return:
        """
        dps = self.apps_v1_api.list_namespaced_deployment(namespace)
        return [i.metadata.name for i in dps.items]

    def get_app_names(self, namespace):
        dps = self.apps_v1_api.list_namespaced_deployment(namespace)
        return list(set([dp.metadata.labels["appName"] for dp in dps.items]))

    def get_deployments(self, namespace):
        """
            获取namespace下所有的dp
        :param namespace:
        :return:
        """
        dps = self.apps_v1_api.list_namespaced_deployment(namespace)
        return dps.items

    def get_deployments_by_label(self, namespace, label_selector):
        kwargs = {
            "label_selector": label_selector
        }
        dps = self.apps_v1_api.list_namespaced_deployment(namespace, **kwargs)
        return dps.items

    def get_deployment_by_field(self, namespace, field_selector):
        kwargs = {
            "field_selector": field_selector
        }
        dps = self.apps_v1_api.list_namespaced_deployment(namespace, **kwargs)
        return [i for i in dps.items]

    @staticmethod
    def fix_dp_metadata(resource, label_k8s_cluster):
        if hasattr(resource.metadata, 'resource_version'):
            resource.metadata.resource_version = None
        if hasattr(resource.metadata, 'uid'):
            resource.metadata.uid = None
        if resource.metadata.annotations and resource.metadata.annotations.get(
                "kubectl.kubernetes.io/last-applied-configuration"):
            resource.metadata.annotations["kubectl.kubernetes.io/last-applied-configuration"] = None
        if hasattr(resource, 'status'):
            resource.status = None
        if "k8sCluster" in resource.metadata.labels.keys():
            resource.metadata.labels["k8sCluster"] = label_k8s_cluster
        if "k8sCluster" in resource.spec.selector.match_labels.keys():
            resource.spec.selector.match_labels["k8sCluster"] = label_k8s_cluster
        if "k8sCluster" in resource.spec.template.metadata.labels.keys():
            resource.spec.template.metadata.labels["k8sCluster"] = label_k8s_cluster

        return resource

    def create_deployment(self, namespace, body):
        try:
            resp = self.apps_v1_api.create_namespaced_deployment(namespace, body, _preload_content=False)
            if resp.status == 201:
                return True
        except Exception as e:
            print(traceback.format_exc(), e)
        return False

    def get_service_names(self, namespace):
        svcs = self.core_v1_api.list_namespaced_service(namespace)
        return [i.metadata.name for i in svcs.items]

    def get_services(self, namespace):
        svcs = self.core_v1_api.list_namespaced_service(namespace)
        return svcs.items

    def get_services_by_label(self, namespace, label_selector):
        kwargs = {
            "label_selector": label_selector
        }
        svcs = self.core_v1_api.list_namespaced_service(namespace, **kwargs)
        return svcs.items

    def get_services_by_field(self, namespace, field_selector):
        kwargs = {
            "field_selector": field_selector
        }
        svcs = self.core_v1_api.list_namespaced_service(namespace, **kwargs)
        return svcs.items

    @staticmethod
    def fix_svc_metadata(resource, label_k8s_cluster):
        if hasattr(resource.metadata, 'resource_version'):
            resource.metadata.resource_version = None
        if resource.metadata.annotations and resource.metadata.annotations.get(
                "kubectl.kubernetes.io/last-applied-configuration"):
            resource.metadata.annotations["kubectl.kubernetes.io/last-applied-configuration"] = None
        if hasattr(resource.metadata, 'uid'):
            resource.metadata.uid = None
        if hasattr(resource, 'status'):
            resource.status = None
        if hasattr(resource.spec, "cluster_ip"):
            resource.spec.cluster_ip = None
        if "k8sCluster" in resource.metadata.labels.keys():
            resource.metadata.labels["k8sCluster"] = label_k8s_cluster
        if "k8sCluster" in resource.spec.selector.keys():
            resource.spec.selector["k8sCluster"] = label_k8s_cluster
        return resource

    def create_services(self, namespace, body):
        try:
            resp = self.core_v1_api.create_namespaced_service(namespace, body, _preload_content=False)
            if resp.status == 201:
                return True
        except Exception as e:
            print(traceback.format_exc(), e)
        return False

    def delete_services(self, namespace, name):
        self.core_v1_api.delete_namespaced_service(name, namespace, _preload_content=False)

    def get_configmap_names(self, namespace):
        cms = self.core_v1_api.list_namespaced_config_map(namespace)
        return [i.metadata.name for i in cms.items]

    def get_configmaps(self, namespace):
        cms = self.core_v1_api.list_namespaced_config_map(namespace)
        return cms.items

    def get_configmap_by_label(self, namespace, label_selector):
        kwargs = {
            "label_selector": label_selector
        }
        cms = self.core_v1_api.list_namespaced_config_map(namespace, **kwargs)
        return cms.items

    def get_configmap_by_field(self, namespace, field_selector):
        kwargs = {
            "field_selector": field_selector
        }
        cms = self.core_v1_api.list_namespaced_config_map(namespace, **kwargs)
        return cms.items

    @staticmethod
    def fix_cm_metadata(resource):
        if hasattr(resource.metadata, 'resource_version'):
            resource.metadata.resource_version = None
        if hasattr(resource.metadata, 'uid'):
            resource.metadata.uid = None
        if hasattr(resource, 'status'):
            resource.status = None
        return resource

    def create_configmap(self, namespace, body):
        try:
            resp = self.core_v1_api.create_namespaced_config_map(namespace, body, _preload_content=False)
            if resp.status == 201:
                return True
        except Exception as e:
            print(traceback.format_exc(), e)
        return False

    def get_secrets(self, namespace):
        sc = self.core_v1_api.list_namespaced_secret(namespace)
        return sc.items

    @staticmethod
    def fix_secrets_metadata(resource):
        if hasattr(resource.metadata, 'resource_version'):
            resource.metadata.resource_version = None
        if hasattr(resource.metadata, 'uid'):
            resource.metadata.uid = None
        if hasattr(resource, 'status'):
            resource.status = None
        return resource

    def create_secrets(self, namespace, body):
        try:
            resp = self.core_v1_api.create_namespaced_secret(namespace, body, _preload_content=False)
            if resp.status == 201:
                return True
        except Exception as e:
            print(traceback.format_exc(), e)
        return False

    def get_ingress_names(self, namespace):
        if "v1.17" in self.get_version():
            api = self.dynamic_api.resources.get(
                api_version="networking.k8s.io/v1beta1",
                kind="Ingress"
            )
            response = api.get(
                namespace=namespace
            )
            return [i.metadata.name for i in response.items]
        ingress = self.net_v1_api.list_namespaced_ingress(namespace)
        return [i.metadata.name for i in ingress.items]

    def get_ingress(self, namespace):
        if "v1.17" in self.get_version():
            api = self.dynamic_api.resources.get(
                api_version="networking.k8s.io/v1beta1",
                kind="Ingress"
            )
            response = api.get(
                namespace=namespace
            )
            return response.items
        ingress = self.net_v1_api.list_namespaced_ingress(namespace)
        return ingress.items

    def get_ingress_by_label(self, namespace, label_selector):
        if "v1.17" in self.get_version():
            api = self.dynamic_api.resources.get(
                api_version="networking.k8s.io/v1beta1",
                kind="Ingress"
            )
            response = api.get(
                namespace=namespace,
                label_selector=label_selector
            )
            return response.items
        kwargs = {
            "label_selector": label_selector
        }
        ingress = self.net_v1_api.list_namespaced_ingress(namespace, **kwargs)
        return ingress.items

    def get_ingress_by_filed(self, namespace, field_selector):
        kwargs = {
            "field_selector": field_selector
        }
        if "v1.17" in self.get_version():
            api = self.dynamic_api.resources.get(
                api_version="networking.k8s.io/v1beta1",
                kind="Ingress"
            )
            response = api.get(
                namespace=namespace,
                field_selector=field_selector
            )
            return response.items
        ingress = self.net_v1_api.list_namespaced_ingress(namespace, **kwargs)
        return ingress.items

    @staticmethod
    def fix_ingress_metadata(resource, label_k8s_cluster):
        if hasattr(resource.metadata, 'resource_version'):
            resource.metadata.resource_version = None
        if hasattr(resource.metadata.annotations, "kubectl.kubernetes.io/last-applied-configuration"):
            setattr(resource.metadata.annotations, "kubectl.kubernetes.io/last-applied-configuration", None)
        if hasattr(resource.metadata, 'uid'):
            resource.metadata.uid = None
        if hasattr(resource, 'status'):
            resource.status = None
        if hasattr(resource.metadata.labels, "k8sCluster"):
            resource.metadata.labels.k8sCluster = label_k8s_cluster
        new_ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": resource.metadata.name,
                "namespace": resource.metadata.namespace,
                "labels": resource.metadata.labels or {},
                "annotations": resource.metadata.annotations or {}
            },
            "spec": {
                "ingressClassName": "nginx",
                "rules": [
                    {
                        "host": rule.host,
                        "http": {
                            "paths": [
                                {
                                    "path": path.path,
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": path.backend.serviceName,
                                            "port": {"number": path.backend.servicePort}
                                        }
                                    }
                                } for path in rule.http.paths
                            ]
                        }
                    } for rule in resource.spec.rules
                ],
                "tls": [{
                    "hosts": [tls_host for tls in resource.spec.tls for tls_host in tls.hosts],
                    "secretName": resource.spec.tls[0].secretName
                }] if hasattr(resource.spec, 'tls') and resource.spec.tls else None
            }
        }
        return eval(str(new_ingress))

    def create_ingress(self, namespace, body):
        try:
            resp = self.net_v1_api.create_namespaced_ingress(namespace, body, _preload_content=False)
            if resp.status == 201:
                return True
        except Exception as e:
            print(traceback.format_exc(), e)
        return False


if __name__ == '__main__':
    # source = {"api_server": "", "namespace": "", "app_name": [], "kind": []}
    source_api_server = ""
    target_api_server = ""

    source_token = CONFIG_SERVER2TOKEN.get(source_api_server)
    source_api_client = InitK8sClient().by_token(source_api_server, source_token)
    source_handle = HandleK8sSource(source_api_client)

    target_token = CONFIG_SERVER2TOKEN.get(target_api_server)
    target_api_client = InitK8sClient().by_token(target_api_server, target_token)
    target_handle = HandleK8sSource(target_api_client)

    #

    app_names = [

    ]

    # app_names = ["biz-cam-hotel-admin-web"]
    _label_k8s_cluster = ""
    _namespace = "fnc"

    # ingress
    # for app_name in app_names:
    #     _label_selector = f"appName={app_name}"
    #     source_ingress = source_handle.get_ingress_by_label(_namespace, _label_selector)
    #     if not source_ingress:
    #         print(f"源集群中:ingress不存在:{app_name}")
    #         continue
    #     for source_ingress_item in source_ingress:
    #         print(f"迁移ingress:{source_ingress_item.metadata.name}")
    #         _new_ingress = source_handle.fix_ingress_metadata(source_ingress_item, _label_k8s_cluster)
    #         target_handle.create_ingress(_namespace, _new_ingress)

    # # svc
    # for app_name in app_names:
    #     _label_selector = f"appName={app_name}"
    #     source_svc = source_handle.get_services_by_label(_namespace, _label_selector)
    #     if not source_svc:
    #         print(f"源集群中,svc不存在:{app_name}")
    #         continue
    #     for source_svc_item in source_svc:
    #         print(f"迁移svc:{source_svc_item.metadata.name}")
    #         _new_svc = source_handle.fix_svc_metadata(source_svc_item, _label_k8s_cluster)
    #         target_handle.create_services(_namespace, _new_svc)

    # dp
    for app_name in app_names:
        _label_selector = f"appName={app_name}"
        source_dp = source_handle.get_deployments_by_label(_namespace, _label_selector)
        if not source_dp:
            print(f"源集群中,dp不存在:{app_name}")
            continue
        for source_dp_item in source_dp:
            print(f"迁移dp:{source_dp_item.metadata.name}")
            _new_dp = source_handle.fix_dp_metadata(source_dp_item, _label_k8s_cluster)
            target_handle.create_deployment(_namespace, _new_dp)
            time.sleep(10)

    # # tct-app_name
    # _namespace = "tct"
    # app_names = source_handle.get_app_names(_namespace)
    # print(app_names)

    # 迁移所有cm
    # _namespace = "fnc"
    # configmaps = source_handle.get_configmaps(_namespace)
    # for configmap in configmaps:
    #     _new_configmap = source_handle.fix_cm_metadata(configmap)
    #     target_handle.create_configmap(_namespace, _new_configmap)

    # 迁移所有的secrets
    # _namespace = "fnc"
    # scs = source_handle.get_secrets(_namespace)
    # for sc in scs:
    #     _new_sc = source_handle.fix_secrets_metadata(sc)
    #     target_handle.create_secrets(_namespace, _new_sc)

    # 迁移所有的configmap
    # source_scs = source_handle.get_secrets(_namespace)
    # target_scs = source_handle.get_secrets(_namespace)
    #
    # print(set([i.metadata.name for i in source_scs])^set([j.metadata.name for j in target_scs]))

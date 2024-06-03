"""
核心资源管理：
Pods：创建、读取、更新、删除Pod，以及查询Pod的状态。
Services：管理服务发现和服务负载均衡，包括创建服务、修改服务端口等。
Deployments & ReplicaSets：部署和管理应用实例，自动扩缩容。
StatefulSets：管理有状态应用，如数据库，支持稳定的网络标识符和存储卷。
DaemonSets：确保每个节点上运行一个指定的Pod副本。
Jobs & CronJobs：一次性任务和定时任务的管理。

配置管理：
ConfigMaps：存储非敏感配置数据，供Pods使用。
Secrets：安全存储敏感信息，如密码、OAuth tokens。

存储管理：
Persistent Volumes (PV) 和 Persistent Volume Claims (PVC)：管理持久化存储资源。

网络管理：
Ingress：配置外部访问到集群内服务的规则。
Network Policies：定义Pod间的网络访问控制策略。

2. 集群管理
命名空间管理：查看、创建、删除命名空间。
节点管理：查看节点状态、标签管理等。
事件和日志：查看Pods、Nodes等资源的事件和日志。
资源配额：设置和管理命名空间内的资源使用限制。

3. 安全与认证
RBAC：管理角色、角色绑定以实现细粒度的权限控制。
Service Accounts：管理服务账户及其权限。

4. 监控与自愈
Health Checks：通过 readinessProbe 和 livenessProbe 配置健康检查。
事件监听与告警：监听Kubernetes事件，可用于自定义监控和告警逻辑。

5. 扩展资源
CRDs (Custom Resource Definitions)：创建和管理自定义资源类型，用于扩展Kubernetes API。

6. 其他高级功能
API资源发现：动态发现API服务器支持的所有资源类型。
Watch API：实时监听资源变化，用于实现事件驱动的编程模型。
Batch Operations：批量操作资源，提高效率。

7. 辅助工具
命令行工具集成：与kubectl命令行工具集成，支持执行kubectl命令。
YAML与JSON转换：在YAML和JSON格式间转换资源定义。
客户端配置：简化与集群的连接配置，支持多种认证方式。
"""
import datetime

"""
core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc
apps_api = client.AppsV1Api()  # 创建deployment.md
networking_api = client.NetworkingV1beta1Api()  # ingress
storage_api = client.StorageV1Api()  # storage_class
"""
from kubernetes import client, config


class KubernetesManager(object):
    """
        CoreV1Api: 对象用于操作 Kubernetes 中的基本资源，这些资源通常是集群的核心组成部分
            Pods
            Services
            ConfigMaps
            Secrets
            PersistentVolumes
            PersistentVolumeClaims
            Nodes
            Events
            Namespaces
            LimitRanges
            ResourceQuotas
            ServiceAccounts
        AppsV1Api: 对象处理与应用程序部署和管理相关的资源，这些资源属于 Kubernetes 的应用层
            Deployments
            StatefulSets
            DaemonSets
            ReplicaSets
            ControllerRevisions
            DeploymentConfigs (OpenShift specific)
        BatchV1Api: 对象主要用于周期性或一次性任务，如批处理作业和cron作业
            Jobs
            CronJobs
        RbacAuthorizationV1Api: 对象处理 Kubernetes 的角色基件授权（RBAC）相关资源
            ClusterRoles
            Roles
            ClusterRoleBindings
            RoleBindings
    """

    def __init__(self):
        config.load_kube_config()
        # configuration = client.Configuration()
        # configuration.host = "https://127.0.0.1:6443"
        # configuration.api_key = {"authorization": "Bearer <YOUR_TOKEN>"}
        # configuration.verify_ssl = False # 如果你的API服务器使用了自签名的证书，你可能需要禁用证书验证
        # client.Configuration.set_default(configuration) # 初始化API客户端

        self.api = client.CoreV1Api()
        self.net_api = client.NetworkingV1Api()

        self.apps_api = client.AppsV1Api()
        self.batch_api = client.BatchV1Api()
        self.rbac_api = client.RbacAuthorizationV1Api()

    def list_namespaces(self):
        """
            查询namespace
        :return:
            ['default', 'kube-node-lease', 'kube-public', 'kube-system']
        """
        namespaces = self.api.list_namespace()
        return [namespace.metadata.name for namespace in namespaces.items]

    def create_namespace(self, namespace_name):
        """
            创建命名空间
        :param namespace_name:
        :return:
            {'api_version': 'v1',
             'kind': 'Namespace',
             'metadata': {'annotations': None,
                          'creation_timestamp': datetime.datetime(2024, 5, 25, 6, 31, 6, tzinfo=tzutc()),
                          'deletion_grace_period_seconds': None,
                          'deletion_timestamp': None,
                          'finalizers': None,
                          'generate_name': None,
                          'generation': None,
                          'labels': {'kubernetes.io/metadata.name': 'test'},
                          'managed_fields': [{'api_version': 'v1',
                                              'fields_type': 'FieldsV1',
                                              'fields_v1': {'f:metadata': {'f:labels': {'.': {},
                                                                                        'f:kubernetes.io/metadata.name': {}}}},
                                              'manager': 'OpenAPI-Generator',
                                              'operation': 'Update',
                                              'subresource': None,
                                              'time': datetime.datetime(2024, 5, 25, 6, 31, 6, tzinfo=tzutc())}],
                          'name': 'test',
                          'namespace': None,
                          'owner_references': None,
                          'resource_version': '39941',
                          'self_link': None,
                          'uid': '310dd93c-b2d7-43ba-b628-12f07124c82f'},
             'spec': {'finalizers': ['kubernetes']},
             'status': {'conditions': None, 'phase': 'Active'}}
        """
        # 定义命名空间的元数据
        metadata = client.V1ObjectMeta(name=namespace_name)
        # 创建命名空间的定义
        namespace = client.V1Namespace(metadata=metadata)
        # 调用API创建命名空间
        response = self.api.create_namespace(namespace)
        return response

    def delete_namespace(self, namespace_name):
        """
            删除namespace
        :param namespace_name:
        :return:
            {'api_version': 'v1',
             'code': None,
             'details': None,
             'kind': 'Namespace',
             'message': None,
             'metadata': {'_continue': None,
                          'remaining_item_count': None,
                          'resource_version': '40447',
                          'self_link': None},
             'reason': None,
             'status': "{'phase': 'Terminating'}"}
        """
        return self.api.delete_namespace(namespace_name)

    def list_nodes(self):
        """
            查看node
        :return:
            ['docker-desktop']
        """
        nodes = self.api.list_node()
        return [node.metadata.name for node in nodes.items]

    def get_all_deployment_in_namespace(self, namespace):
        """
            获取指定namespace下的所有deployment
        :param namespace:
        :return:
            ['nginx-创建deployment.md']
        """
        deployments = self.apps_api.list_namespaced_deployment(namespace=namespace)
        return [i.metadata.name for i in deployments.items]

    def get_deployment_by_name(self, namespace, deployment_name):
        """
            指定namespace和deployment名称获取deployment
        :param namespace:
        :param deployment_name:
        :return:
        """
        deployment = self.apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        return deployment

    def get_deployment_by_label(self, namespace, label_selector):
        """
            指定namespace和标签获取deployment
        :param namespace:
        :param label_selector: app=my-app
        :return:
            ['nginx-创建deployment.md']
        """
        deployments = self.apps_api.list_namespaced_deployment(namespace=namespace, label_selector=label_selector)
        return [i.metadata.name for i in deployments.items]

    def create_deployment(self, namespace, deployment_name, replicas, image):
        """
            初始化创建deployment
        :param namespace:
        :param deployment_name:
        :param replicas:
        :param image:
        :return:
        """
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": deployment_name,
                "labels": {"app": "my-app"}
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {"app": "my-app1"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "my-app"}
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "my-container",
                                "image": image,
                                "ports": [{"containerPort": 80}]
                            }
                        ]
                    }
                }
            }
        }
        deployment = self.apps_api.create_namespaced_deployment(namespace=namespace, body=deployment_manifest)
        return deployment

    def delete_deployment(self, namespace, deployment_name):
        """
            删除deployment
        :param namespace: 命名空间
        :param deployment_name:
        :return:
            {'api_version': 'v1',
             'code': None,
             'details': {'causes': None,
                         'group': 'apps',
                         'kind': 'deployments',
                         'name': '创建deployment.md-test',
                         'retry_after_seconds': None,
                         'uid': '290f869d-2312-433e-8b5a-c1f656b66b92'},
             'kind': 'Status',
             'message': None,
             'metadata': {'_continue': None,
                          'remaining_item_count': None,
                          'resource_version': None,
                          'self_link': None},
             'reason': None,
             'status': 'Success'}
        """
        return self.apps_api.delete_namespaced_deployment(name=deployment_name, namespace=namespace)

    def scale_deployments(self, namespace, deployment_name, replicas):
        """
            扩容
        :param namespace:
        :param deployment_name:
        :param replicas: 数量
        :return:
            {'api_version': 'autoscaling/v1',
             'kind': 'Scale',
             'metadata': {'annotations': None,
                          'creation_timestamp': datetime.datetime(2024, 5, 27, 12, 19, 10, tzinfo=tzutc()),
                          'deletion_grace_period_seconds': None,
                          'deletion_timestamp': None,
                          'finalizers': None,
                          'generate_name': None,
                          'generation': None,
                          'labels': None,
                          'managed_fields': None,
                          'name': '创建deployment.md-test',
                          'namespace': 'default',
                          'owner_references': None,
                          'resource_version': '51544',
                          'self_link': None,
                          'uid': '45768f0b-1676-4b5a-b96d-9b9b3213c162'},
             'spec': {'replicas': 3},
             'status': {'replicas': 2, 'selector': 'app=my-app1'}}
        """
        body = {"spec": {"replicas": replicas}}
        return self.apps_api.patch_namespaced_deployment_scale(name=deployment_name, namespace=namespace, body=body)

    def restart_deployment(self, namespace, deployment_name):
        """
            重启deployment
            patch_namespaced_deployment这里只要更改对应的值即可
        :param namespace:
        :param deployment_name:
        :return:
        """
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": str(datetime.datetime.now())
                        }
                    }
                }
            }
        }
        # patch_namespaced_deployment
        return self.apps_api.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=body)

    def create_namespaced_service(self, namespace, body, **kwargs):
        """
            创建service
        :param namespace: namespace
        :param body: {}
        :return:
        """
        return self.api.create_namespaced_service(namespace=namespace, body=body, **kwargs)

    def list_namespaced_service(self, namespace, **kwargs):
        """
            列出service
        :param namespace:
        :return:
        """
        services = self.api.list_namespaced_service(namespace=namespace, **kwargs)
        return [i.metadata.name for i in services.items]

    def delete_namespaced_service(self, name, namespace, **kwargs):
        """
            删除service
        :param name:
        :param namespace:
        :return:
        """
        return self.api.delete_namespaced_service(name=name, namespace=namespace, **kwargs)

    def patch_namespaced_service(self, name, namespace, body, **kwargs):
        """
            修改namespace的service
        :param name:
        :param namespace:
        :param body:
        :return:
        """
        return self.api.patch_namespaced_service(name=name, namespace=namespace, body=body, **kwargs)

    def create_namespaced_pod(self, namespace, body, **kwargs):
        """
            创建pod
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.create_namespaced_pod(namespace=namespace, body=body, **kwargs)

    def list_namespaced_pod(self, namespace_name, **kwargs):
        """
            列出pod
        :param namespace_name: namespace
        :return:
        """
        pods = self.api.list_namespaced_pod(namespace=namespace_name, **kwargs)
        return [i.metadata.name for i in pods.items]

    def delete_namespaced_pod(self, name, namespace, **kwargs):
        """
            删除pod
        :param name:
        :param namespace:
        :param kwargs:
        :return:
        """
        return self.api.delete_namespaced_pod(name=name, namespace=namespace, **kwargs)

    def patch_namespaced_pod(self, name, namespace, body, **kwargs):
        """
            修改namespace的pod
        :param name:
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.patch_namespaced_pod(name=name, namespace=namespace, body=body, **kwargs)

    def get_pod_logs(self, pod_name, namespace="default", follow=False, tail_lines=10):
        """
            查看pod日志
        :param pod_name:
        :param namespace:
        :param follow:
        :param tail_lines:
        :return:
        """
        stream_method = self.api.read_namespaced_pod_log if not follow else self.api.read_namespaced_pod_log
        log_output = stream_method(
            name=pod_name,
            namespace=namespace,
            follow=follow,
            tail_lines=tail_lines
        )
        for line in log_output:
            print(line.decode('utf-8'))

    def list_namespaced_secret(self, namespace, **kwargs):
        """
            查看secret
        :param namespace:
        :param kwargs:
        :return:
        """
        return self.api.list_namespaced_secret(namespace=namespace, **kwargs)

    def create_namespaced_secret(self, namespace, body, **kwargs):
        """
            创建secret
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.create_namespaced_secret(namespace=namespace, body=body, **kwargs)

    def delete_namespaced_secret(self, name, namespace, **kwargs):
        """
            删除secret
        :param name:
        :param namespace:
        :param kwargs:
        :return:
        """
        return self.api.delete_namespaced_secret(name=name, namespace=namespace, **kwargs)

    def patch_namespaced_secret(self, name, namespace, body, **kwargs):
        """
            修改secret
        :param name:
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.patch_namespaced_secret(name=name, namespace=namespace, body=body, **kwargs)

    def list_namespaced_config_map(self, namespace, **kwargs):
        """
            查看config-map
        :param namespace:
        :param kwargs:
        :return:
        """
        return self.api.list_namespaced_config_map(namespace=namespace, **kwargs)

    def create_namespaced_config_map(self, namespace, body, **kwargs):
        """
            创建config-Map
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.create_namespaced_config_map(namespace=namespace, body=body, **kwargs)

    def delete_namespaced_config_map(self, name, namespace, **kwargs):
        """
            删除config-map
        :param name:
        :param namespace:
        :param kwargs:
        :return:
        """
        return self.api.delete_namespaced_config_map(name=name, namespace=namespace, **kwargs)

    def patch_namespaced_config_map(self, name, namespace, body, **kwargs):
        """
            修改config-map
        :param name:
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.patch_namespaced_config_map(name=name, namespace=namespace, body=body, **kwargs)

    def list_persistent_volume(self, **kwargs):
        """
            列出pv
        :param kwargs:
        :return:
        """
        return self.api.list_persistent_volume(**kwargs)

    def create_persistent_volume(self, body, **kwargs):
        """
            创建pv
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.create_persistent_volume(body=body, **kwargs)

    def delete_persistent_volume(self, name, **kwargs):
        """
            删除pv
        :param name:
        :param kwargs:
        :return:
        """
        return self.api.delete_persistent_volume(name=name, **kwargs)

    def patch_persistent_volume(self, name, body, **kwargs):
        """
            修改pv
        :param name:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.patch_persistent_volume(name=name, body=body, **kwargs)

    def list_persistent_volume_claim_for_all_namespaces(self, **kwargs):
        """
            列出pvc
        :param kwargs:
        :return:
        """
        return self.api.list_persistent_volume_claim_for_all_namespaces(**kwargs)

    def patch_namespaced_persistent_volume_claim(self, name, namespace, body, **kwargs):
        """
            修改pvc
        :param name:
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.api.patch_namespaced_persistent_volume_claim(name=name, namespace=namespace, body=body, **kwargs)

    def list_namespaced_ingress(self, namespace, **kwargs):
        """
            列举指定namespace下的ingress
        :param namespace:
        :param kwargs:
        :return:
        """
        return self.net_api.list_namespaced_ingress(namespace, **kwargs)

    def create_namespaced_ingress(self, namespace, body, **kwargs):
        """
            创建指定namespace下的ingress.
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.net_api.create_namespaced_ingress(namespace, body, **kwargs)

    def delete_namespaced_ingress(self, name, namespace, **kwargs):
        """
            删除指定namespace下的ingress
        :param name:
        :param namespace:
        :param kwargs:
        :return:
        """
        return self.net_api.delete_namespaced_ingress(name, namespace, **kwargs)

    def patch_namespaced_ingress(self, name, namespace, body, **kwargs):
        """
            修改指定namespace下的ingress.
        :param name:
        :param namespace:
        :param body:
        :param kwargs:
        :return:
        """
        return self.net_api.patch_namespaced_ingress(name, namespace, body, **kwargs)


# 示例
if __name__ == "__main__":
    k = KubernetesManager()
    # print(k.list_namespaces())
    _namespace_name = "test"
    # print(k.create_namespace(_namespace_name))
    # print(k.delete_namespace(_namespace_name))
    # print(k.list_nodes())
    # print(k.get_all_deployment_in_namespace(_namespace_name))
    # print(k.get_deployment_by_name(_namespace_name, "创建deployment.md-test"))
    # print(k.get_deployment_by_label(_namespace_name, "app=my-app"))
    # print(k.create_deployment(_namespace_name, "创建deployment.md-test", 2, "nginx:latest"))
    # print(k.delete_deployment(_namespace_name, "创建deployment.md-test"))
    # print(k.scale_deployments(_namespace_name, "创建deployment.md-test", 3))
    # print(k.restart_deployment(_namespace_name, "创建deployment.md-test"))
    # print(k.list_namespaced_pod(_namespace_name, "app=my-app1"))

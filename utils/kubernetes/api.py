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

"""
core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc
apps_api = client.AppsV1Api()  # deployment
networking_api = client.NetworkingV1beta1Api()  # ingress
storage_api = client.StorageV1Api()  # storage_class
"""
from kubernetes import client, config
import json

# 加载 Kubernetes 配置文件（kubeconfig）
config.load_kube_config()

# 创建 Kubernetes 客户端对象
v1 = client.CoreV1Api()

# Service 的 JSON 定义
service_json = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": "my-service"
    },
    "spec": {
        "selector": {
            "app": "my-app"
        },
        "ports": [
            {
                "protocol": "TCP",
                "port": 80,
                "targetPort": 9376
            }
        ]
    }
}


# 创建 Service
def create_service():
    return v1.create_namespaced_service(namespace="default", body=service_json)


# 列出所有 Service
def list_services():
    return v1.list_namespaced_service(namespace="default")


# 删除 Service
def delete_service(service_name):
    return v1.delete_namespaced_service(name=service_name, namespace="default")


config.load_kube_config()

# 创建 Kubernetes 客户端对象
v1 = client.CoreV1Api()


# 创建 Pod
def create_pod():
    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "my-pod"
        },
        "spec": {
            "containers": [
                {
                    "name": "my-container",
                    "image": "nginx",
                    "ports": [
                        {
                            "containerPort": 80
                        }
                    ]
                }
            ]
        }
    }
    return v1.create_namespaced_pod(namespace="default", body=pod_manifest)


# 读取 Pod
def read_pod(pod_name):
    return v1.read_namespaced_pod(name=pod_name, namespace="default")


# 更新 Pod
def update_pod(pod_name):
    pod = read_pod(pod_name)
    pod.spec.containers[0].image = "nginx:latest"
    return v1.replace_namespaced_pod(name=pod_name, namespace="default", body=pod)


# 删除 Pod
def delete_pod(pod_name):
    return v1.delete_namespaced_pod(name=pod_name, namespace="default")


# 查询 Pod 状态
def get_pod_status(pod_name):
    pod = read_pod(pod_name)
    return pod.status.phase


from kubernetes import client, config


def get_deployment_info(deployment_name):
    config.load_kube_config()
    api_instance = client.AppsV1Api()
    response = api_instance.read_namespaced_deployment(name=deployment_name, namespace="default")
    print(f"Deployment '{deployment_name}' details: {response.to_dict()}")


def create_deployment():
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()

    deployment_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "my-new-deployment"},
        "spec": {
            "replicas": 3,
            "selector": {"matchLabels": {"app": "my-app"}},
            "template": {
                "metadata": {"labels": {"app": "my-app"}},
                "spec": {
                    "containers": [
                        {
                            "name": "my-container",
                            "image": "nginx:latest",
                            "ports": [{"containerPort": 80}]
                        }
                    ]
                }
            }
        }
    }
    apps_v1_api.create_namespaced_deployment(body=deployment_manifest, namespace="default")


def scale_deployment(deployment_name, replicas):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    body = {"spec": {"replicas": replicas}}
    apps_v1_api.patch_namespaced_deployment_scale(name=deployment_name, namespace="default", body=body)


def pause_deployment(deployment_name):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    patch_body = {"spec": {"paused": True}}
    apps_v1_api.patch_namespaced_deployment(name=deployment_name, namespace="default", body=patch_body)


def resume_deployment(deployment_name):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    patch_body = {"spec": {"paused": False}}
    apps_v1_api.patch_namespaced_deployment(name=deployment_name, namespace="default", body=patch_body)


def delete_deployment(deployment_name):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    apps_v1_api.delete_namespaced_deployment(name=deployment_name, namespace="default", body=client.V1DeleteOptions())


from kubernetes import client, config


def create_replicaset():
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()

    replicaset_manifest = {
        "apiVersion": "apps/v1",
        "kind": "ReplicaSet",
        "metadata": {"name": "my-replicaset"},
        "spec": {
            "replicas": 3,
            "selector": {"matchLabels": {"app": "my-app"}},
            "template": {
                "metadata": {"labels": {"app": "my-app"}},
                "spec": {
                    "containers": [{"name": "my-container", "image": "nginx"}]
                },
            },
        },
    }

    apps_v1_api.create_namespaced_replica_set(namespace="default", body=replicaset_manifest)


# create_replicaset()


def get_replicaset(name):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    replicaset = apps_v1_api.read_namespaced_replica_set(name, "default")
    print(f"ReplicaSet '{name}': {replicaset.to_dict()}")


# get_replicaset("my-replicaset")
def update_replicas(replicaset_name, replicas):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    body = {"spec": {"replicas": replicas}}
    apps_v1_api.patch_namespaced_replica_set(name=replicaset_name, namespace="default", body=body)


# update_replicas("my-replicaset", 5)
def delete_replicaset(replicaset_name):
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    apps_v1_api.delete_namespaced_replica_set(name=replicaset_name, namespace="default", body=client.V1DeleteOptions())


# delete_replicaset("my-replicaset")


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

    def list_namespaced_pod(self, namespace_name):
        pods = self.api.list_namespaced_pod(namespace=namespace_name)
        return pods

    def get_pod_logs(self, pod_name, namespace="default", follow=False, tail_lines=10):
        stream_method = self.api.read_namespaced_pod_log if not follow else self.api.read_namespaced_pod_log
        log_output = stream_method(
            name=pod_name,
            namespace=namespace,
            follow=follow,
            tail_lines=tail_lines
        )

        for line in log_output:
            print(line.decode('utf-8'))

    def get_all_deployment_in_namespace(self, namespace):
        """
            获取指定namespace下的所有deployment
        :param namespace:
        :return:
            ['nginx-deployment']
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
            ['nginx-deployment']
        """
        deployments = self.apps_api.list_namespaced_deployment(namespace=namespace, label_selector=label_selector)
        return [i.metadata.name for i in deployments.items]

    def create_deplpyment(self, namespace, deployment_name, replicas, image):
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": deployment_name},
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": "my-app1"}},
                "template": {
                    "metadata": {"labels": {"app": "my-app1"}},
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


# 示例
if __name__ == "__main__":
    k = KubernetesManager()
    # print(k.list_namespaces())
    _namespace_name = "test"
    # print(k.create_namespace(_namespace_name))
    # print(k.delete_namespace(_namespace_name))
    # print(k.list_nodes())
    # print(k.get_all_deployment_in_namespace("default"))
    # print(k.get_deployment_by_name("default", "nginx-deployment"))
    # print(k.get_deployment_by_label("default", "app=my-app"))
    # print(k.create_deplpyment("default","deployment-test", 2, "nginx:latest"))
    pass
    # 创建 Service
    # create_service()
    # print("Service created.")
    #
    # # 列出所有 Service
    # print("\nList of Services:")
    # print(list_services())
    # for svc in list_services().items:
    #     print("- ", svc.metadata.name)

    # # 删除 Service
    # delete_service("my-service")
    # print("\nService deleted.")

    # print(create_pod())

    # print(read_pod("my-pod"))

    # print(update_pod("my-pod"))

    # print(get_pod_status("my-pod"))

    # print(delete_pod("my-pod"))

    # create_deployment()

    # scale_deployment("my-new-deployment",4)

    # print(pause_deployment("my-new-deployment"))

    # print(delete_deployment("my-new-deployment"))

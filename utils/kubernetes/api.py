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

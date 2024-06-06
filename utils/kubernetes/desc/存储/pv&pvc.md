#### PersistentVolume (PV):
* PV是集群管理员预配置的存储资源，它代表了实际的存储实体，如硬盘、网络存储(NFS、Ceph等)或云提供商的存储服务。
* PV具有固定的容量、访问模式（如读写、只读）和存储类（StorageClass）等属性。
* PV的生命周期独立于Pod，即使Pod被删除，数据仍然保留。
* PV是一种静态资源，通常通过YAML文件定义，并使用kubectl create命令创建。
#### PersistentVolumeClaim (PVC):
* PVC是用户或应用请求存储资源的方式，它定义了所需的存储容量和访问模式。
* PVC是动态的，由Pod或其配置文件创建，用来声明对PV的需求。
* 当PVC被创建时，Kubernetes调度器会尝试找到一个匹配的PV来绑定（如果存在未使用的PV满足PVC的要求）。
* PVC也可以与StorageClass关联，允许动态Provisioning，即当PVC创建时自动创建相应的PV。

> 总结来说，PV是存储的供应方，而PVC是存储的需求方。PVC提供了声明式的方式来管理存储，使得用户无需直接操作底层存储资源，只需声明所需，Kubernetes会负责匹配和管理。
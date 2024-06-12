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

#### pv和pvc如何关联

##### 动态供给（Dynamic Provisioning）:
* 当用户创建一个 PVC 并指定了一个 storageClassName 时，Kubernetes 会查找与该类名匹配的 StorageClass。
* 如果找到了匹配的 StorageClass，并且该类配置为动态供给，Kubernetes 会自动创建一个 PV，其特性与 StorageClass 定义的相匹配。
* 这个新创建的 PV 会被自动绑定到 PVC 上，完成关联。
  
##### 静态供给（Static Provisioning）
* 对于静态创建的 PV，管理员事先定义好 PV，包括其容量、访问模式和存储类型等。
* 用户创建 PVC 时，可以通过请求的存储大小、访问模式和（可选的）存储类来表达需求。
* Kubernetes 的控制器会尝试找到一个匹配的 PV（考虑容量、访问模式、存储类等因素）并与 PVC 绑定。如果 PV 的 storageClassName 与 PVC 中请求的相匹配，或者 PVC 没有指定存储类而 PV 是默认的存储类，则认为是匹配的。
* 一旦找到合适的 PV，PVC 就会被标记为 “Bound” 状态，同时 PV 也会更新其绑定信息，表示已被 PVC 使用。

##### 匹配与绑定
* PV 和 PVC 的匹配过程基于多种条件，包括存储大小（PV 的容量需大于等于 PVC 的请求量）、访问模式（PV 支持的访问模式需包含 PVC 所请求的模式）以及存储类。
* 如果有多个 PV 都能满足 PVC 的需求，Kubernetes 会选择最合适的 PV 进行绑定。在某些情况下，可以通过标签选择器（label selectors）进一步细化匹配规则，让 PV 仅能被具有特定标签的 PVC 绑定
  
##### 预绑定（Pre-Binding
* 在某些特殊场景下，管理员可能希望预定义 PV 与特定 PVC 的绑定关系，这可以通过直接在 PV 的定义中指定 .spec.claimRef 字段来实现，明确指定该 PV 应该绑定到哪个 PVC
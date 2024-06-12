#### 动态供给（Dynamic Provisioning）：
* StorageClass 最重要的功能之一是支持存储的动态供给。这意味着当用户创建一个 PersistentVolumeClaim (PVC) 并指定一个 StorageClass 时，Kubernetes 会自动创建一个符合需求的 PersistentVolume (PV)，而不需要手动预配置每个 PV。这一过程简化了存储资源的管理和分配。
#### 资源分类：
* 它提供了一种方式来区分和分类存储资源，比如基于性能（如SSD与HDD）、成本、备份策略或地理位置等因素。这样，应用程序可以根据其需求选择合适的存储类别。
#### 配置选项：
* StorageClass 定义了一系列参数，这些参数指导了如何创建和配置 PV。例如，可以设置存储的大小限制、访问模式（如读写一次、只读多次）以及特定于供应商的配置选项。
#### 默认存储类：
* 可以为集群设置一个默认的 StorageClass。当用户创建 PVC 而没有明确指定 StorageClass 时，系统会自动使用这个默认类来创建 PV。
#### 与外部存储集成：
* StorageClass 支持与各种外部存储系统集成，如云提供商的块存储服务（如AWS EBS、GCP PD）、NFS、Ceph等，通过不同的插件或provisioners实现。
#### 声明式管理：
* 通过 YAML 文件定义 StorageClass，与 Kubernetes 的声明式配置风格保持一致，便于版本控制和自动化部署。

#### 属性配置
* `provisioner`：指定负责创建 PV 的外部存储插件或系统，如 AWS EBS、GCE PD、NFS 等。
* `parameters`：提供给 provisioner 的参数，用于定制存储卷，例如磁盘类型、IOPS 等。
* `reclaimPolicy`：决定当 PVC 被删除时，PV 的数据应如何处理，通常是 Retain（保留数据）、Delete（删除数据

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  # StorageClass 的名称
  name: managed-nfs-storage
  # 可选的注解，例如设置为默认的 StorageClass
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: example.com/nfs # 这里应替换为实际的 provisioner 名称，如kubernetes.io/nfs对于NFS
# 可选参数，传递给底层存储系统
parameters:
  # NFS 服务器地址
  server: nfs.example.com
  # 共享目录路径
  path: "/exports/data"

# reclaimPolicy 定义了 PersistentVolume 在 PVC 被删除时的行为
reclaimPolicy: Delete
# 可选的卷绑定模式，如动态绑定 (Dynamic) 或立即绑定 (Immediate)
volumeBindingMode: Immediate
```
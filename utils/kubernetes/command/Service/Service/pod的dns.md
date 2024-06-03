#### Service 的 DNS 解析:
* Service 名称作为 DNS 域名：当你创建一个 Service 时，它会得到一个唯一的 DNS 名称，通常是 <service-name>.<namespace>.svc.cluster.local。例如，如果有一个名为 web 的 Service 在 default 命名空间中，它的 DNS 名称就是 web.default.svc.cluster.local。
* 服务发现：Pods 可以通过这个 DNS 名称来发现并连接到 Service，无需知道具体的 Pod IP 地址。
* 负载均衡：DNS 解析返回的是 Service 的虚拟 IP（VIP，Virtual IP），这个 VIP 会负载均衡到后端的 Pods。
  
#### Pod 的 DNS 解析
* Pod 的 DNS 设置：默认情况下，每个 Pod 的 /etc/resolv.conf 文件会被配置为使用集群的 DNS 服务器，通常是 CoreDNS 或 kube-dns。
* Pod 自身的 DNS：Pod 内部的应用程序可以通过 DNS 查找其他 Service 或 Pod。对于查找其他 Service，可以直接使用 Service 的 DNS 名称。对于查找其他 Pod，如果 Pod 有 DNS 名称（例如，通过 dnsPolicy: ClusterFirstWithHostNet 创建的 Pod），也可以直接通过 Pod 的 DNS 名称进行查找。
* 命名空间的隔离：DNS 查询会考虑命名空间，这意味着一个 Pod 只能直接通过 DNS 查找相同命名空间内的 Service 或 Pod，除非使用完全限定域名（FQDN）
  

#### DNS Policy：
* Pod 的 dnsPolicy 字段决定了其 DNS 解析行为。默认是 ClusterFirst，意味着首先查找集群内的 DNS 记录，如果找不到再查找外部 DNS。
* Default 政策则使 Pod 使用节点的 DNS 设置。
* None 政策允许自定义 DNS 配置。
* ClusterFirstWithHostNet 用于 Pod 使用 hostNetwork，同时允许访问集群 DNS 和宿主机 DNS。
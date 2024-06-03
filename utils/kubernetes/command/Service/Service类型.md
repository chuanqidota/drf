#### ClusterIP
* 特点：这是默认的 Service 类型，它为 Service 分配一个内部的、集群范围的 IP 地址，只能从集群内部访问。
* 使用场景：适用于仅需在集群内部通信的服务，不对外暴露，提供服务间的通信。


#### NodePort
* 特点：在每个节点（worker node）上打开一个静态的端口，外部可以通过 NodeIP:NodePort 访问 Service。
* 使用场景：当需要从集群外部访问服务，但不需要或不支持负载均衡器时，可以通过节点的 IP 和配置的端口来访问


#### LoadBalancer
* 特点：在云环境中，它会创建一个外部负载均衡器（如 AWS ELB、GCP Load Balancer 等），并将流量路由到 Service。
* 使用场景：适用于需要公开、受控地从互联网访问服务的情况，通常由云提供商提供负载均衡功能。
  
#### ExternalName
* 特点：它将 Service 映射到一个外部 DNS 名称，不创建任何内部 IP 地址，而是返回 CNAME 记录指向指定的域名。
* 使用场景：用于将 Kubernetes 内部的请求直接转发到外部服务，不涉及集群内的 Pod。
  
#### 访问
* 在集群内部通过 $(ClusterIP): $(Port) 访问
* 在集群外部通过 $(NodeIP): $(NodePort) 访问
* 在集群外部通过 $(LoadBalancerIP): $(Port) 访问

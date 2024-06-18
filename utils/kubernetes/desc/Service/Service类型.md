#### ClusterIP
* 特点：这是默认的 Service 类型，它为 Service 分配一个内部的、集群范围的 IP 地址，只能从集群内部访问。
* 使用场景：适用于仅需在集群内部通信的服务，不对外暴露，提供服务间的通信。
* 访问方式：可以创建一个pod,然后访问http://<server_name>,如果跨命名空间访问，则是http://<server_name>.<namespace>
```yaml
# 定义一个可以集群内部访问的service
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: default
spec:
  type: ClusterIP # 这里定义了服务类型为ClusterIP
  selector: # 用于选择后端Pod的标签
    app: my-app
  ports:
    - name: http
      port: 80 # service端口，在集群内部访问该服务的端口
      targetPort: 8080 # pod端口，后端pod实际监听的端口
```
* 访问方式2: 如果yaml文件中不指明selector,则需要手动创建endpoint,这时候讲endpoint地址改到外部，就可以通过访问server访问外部服
```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-service
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: 8080
```
接着，创建一个Endpoints资源来指定服务的实际后端地址。这里我们可以列出外部IP地址及其端口：
```yaml
apiVersion: v1
kind: Endpoints
metadata:
  name: external-service
subsets:
  - addresses:
      - ip: 192.168.1.100 # 外部IP地址示例
    ports:
      - port: 8080 # 对应服务期望访问的端口
```
在这个例子中，我们创建了一个没有与之匹配的Pod标签的Service，并单独定义了一个Endpoints资源，其中包含了具体的外部IP地址和端口。这样，集群内的服务就可以通过之前定义的ClusterIP服务名来访问这个外部地址了

#### NodePort
* 特点：在每个节点（worker node）上打开一个静态的端口，外部可以通过 NodeIP:NodePort 访问 Service。
* 使用场景：当需要从集群外部访问服务，但不需要或不支持负载均衡器时，可以通过节点的 IP 和配置的端口来访问
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
  labels:
    app: my-app
spec:
  type: NodePort # 指定服务类型为NodePort
  selector: # 用于选择后端Pod的标签
    app: my-app
  ports:
    - name: http
      protocol: TCP
      port: 80 # 服务端口，在集群内部访问该服务的端口
      targetPort: 8080 # Pod端口，后端pod实际监听的端口
      nodePort: 30080 # 指定将在每个节点上开放的端口，供外部访问
```
服务可以通过任意节点的 <节点IP>:30080 访问（假设 nodePort 设置为30080）

#### LoadBalancer
* 特点：在云环境中，它会创建一个外部负载均衡器（如 AWS ELB、GCP Load Balancer 等），并将流量路由到 Service。
* 使用场景：适用于需要公开、受控地从互联网访问服务的情况，通常由云提供商提供负载均衡功能。
  
#### ExternalName
* 特点：它将 Service 映射到一个外部 DNS 名称，不创建任何内部 IP 地址，而是返回 CNAME 记录指向指定的域名。这种方式不需要创建任何集群内部的Endpoint或Pod，而是直接利用DNS解析将服务名指向外部域名
* 使用场景：用于将 Kubernetes 内部的请求直接转发到外部服务，不涉及集群内的 Pod。
* 使用方式：集群内部创建一个pod,然后访问http://<server_name>就会转发到外部的域名上
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-externalname-service
spec:
  type: ExternalName # 指定服务类型为ExternalName
  externalName: example.service.com # 想要映射到的外部域名
```
应用这个配置后，Kubernetes集群内的服务和Pod可以通过服务名 http://my-externalname-service 直接访问到 example.service.com，就像访问集群内部服务一样


#### 访问
* 在集群内部通过 $(ClusterIP): $(Port) 访问
* 在集群外部通过 $(NodeIP): $(NodePort) 访问
* 在集群外部通过 $(LoadBalancerIP): $(Port) 访问

#### 就绪探针 (Readiness Probe):
* 目的：确定容器是否准备好接收流量。只有当就绪探针成功时，服务才会被 Service 路由到该容器，确保客户端只访问到能够正常响应的实例。
* 应用场景：适合在容器启动初期或重启后，等待应用完全加载完毕再开始接受请求，避免半初始化状态影响用户体验

#### demo
* 对于同样的服务，我们也可以设置就绪探针来确保服务准备好接收请求。
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
  - name: myapp-container
    image: myapp:v1
    readinessProbe:
      httpGet:
        path: /readiness
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 2
```
> 这里，Kubernetes 会定期（每隔2秒）检查/readiness路径，首次检查在容器启动后10秒开始。如果探测成功，表示容器已准备好服务，否则不会将其添加到Service的负载均衡池中
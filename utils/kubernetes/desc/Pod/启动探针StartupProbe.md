#### 启动探针 (Startup Probe):
* 目的：专门用于检查容器在启动过程中的进度，直到应用程序完全初始化完成。如果启动探针在指定时间内没有成功，Kubernetes 可能会终止容器并根据重启策略处理。
* 应用场景：适用于启动时间较长的应用，避免在应用程序完全启动之前就绪探针误判容器未准备好而影响服务发现和负载均衡

#### demo
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
  - name: myapp-container
    image: myapp:v1
    startupProbe:
      httpGet:
        path: /startup-check
        port: 8080
      failureThreshold: 30
      periodSeconds: 5

```
> 在这个场景中，Kubernetes 会每5秒检查一次/startup-check路径，允许失败最多30次（即最多150秒），如果在此期间探测成功，则认为启动完成，之后就绪探针和存活探针将接管容器的健康监测
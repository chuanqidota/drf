##### 存活探针 (Liveness Probe):
* 目的：检查容器是否正在运行并且处于健康状态。如果存活探针失败，表明容器可能已经卡死或者进入了某种故障状态，Kubernetes 将会终止这个容器，并根据重启策略决定是否重新启动它。 
* 应用场景：适用于检测应用程序是否能够响应或者容器内部状态是否正常，防止“僵尸”进程占用资源。


##### demo:
* 假设我们有一个基于HTTP的服务，我们可以通过检查其健康检查端点来确定服务是否存活
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
  - name: myapp-container
    image: myapp:v1
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 5
```
> 在这个例子中，Kubernetes 每隔5秒 (periodSeconds) 向容器的8080端口上的/healthz路径发送一个GET请求，首次检查在容器启动后15秒 (initialDelaySeconds) 开始。如果连续多次探测无响应或响应失败，则认为容器不健康并采取相应行动（如重启）
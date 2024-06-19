##### 使用场景
* 共享卷中的特定文件: 当一个卷被多个容器共享时，每个容器可能只需要访问该卷上的特定文件或目录，而不是整个卷内容。
* 避免文件覆盖: 如果容器需要在挂载点下写入文件，但又不想覆盖挂载的整个目录，可以使用 subPath 指定写入的子目录或文件。
* 配置文件更新: 更新应用配置时，可以仅替换配置文件而不影响其他同卷挂载的文件

假设你有一个卷包含了多个配置文件，而你的应用容器只需要使用其中一个配置文件。
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
  - name: myapp-container
    image: myapp:v1
    volumeMounts:
    - name: config-volume
      mountPath: /etc/app/config
      subPath: app.conf  # 指定只挂载卷中的app.conf文件
  volumes:
  - name: config-volume
    configMap:
      name: myapp-config  # 假设有一个名为myapp-config的ConfigMap
```
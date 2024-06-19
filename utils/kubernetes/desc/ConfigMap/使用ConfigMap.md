#### 使用ConfigMap
在 Pod 的定义中，可以通过环境变量引用 ConfigMap 的值
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: someimage
    env:
    - name: MY_VAR
      valueFrom:
        configMapKeyRef:
          name: example-configmap # configmap的名称
          key: property1 # configmap中的键值key
```

###### 作为Volume挂载
将 ConfigMap 挂载为 Pod 的 Volume，让应用直接读取文件：
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-pod
spec:
  containers:
  - name: my-container
    image: my-app-image
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config  # 指定容器内挂载路径
      readOnly: true          # 可选，设置为只读
  volumes:
  - name: config-volume      # 必须与volumeMounts中的name对应
    configMap:
      name: my-config-map   # ConfigMap的名称
      items:                 # 可选，如果需要映射ConfigMap中的特定key到文件
      - key: application.properties
        path: app.properties  # 容器内的文件名
```
在这个例子中，我们定义了一个Pod名为my-app-pod，它包含一个容器my-container。这个容器从Docker镜像my-app-image启动，并且挂载了一个名为config-volume的Volume，该Volume的数据来源于名为my-config-map的ConfigMap。

* volumeMounts部分指定了在容器内部如何挂载这个Volume，这里选择的路径是/etc/config。
* volumes部分定义了Volume来源，这里使用的是configMap类型，并指定了ConfigMap的名称为my-config-map。
* items数组是可选的，用于映射ConfigMap中的具体键到容器内的特定文件路径。如果省略，ConfigMap的所有键值对默认会被扁平化到挂载目录
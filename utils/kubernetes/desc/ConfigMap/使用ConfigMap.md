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
          name: example-configmap
          key: property1
```

###### 作为Volume挂载
将 ConfigMap 挂载为 Pod 的 Volume，让应用直接读取文件：
```yaml
volumeMounts:
- name: config-volume
  mountPath: /etc/config
volumes:
- name: config-volume
  configMap:
    name: example-configmap
```
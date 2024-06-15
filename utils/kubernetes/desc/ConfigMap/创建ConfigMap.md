#### 创建ConfigMap

##### 从字面量创建
可以直接使用命令行创建包含键值对的 ConfigMap：
```bash
kubectl create configmap <configmap-name> \
    --from-literal=key1=value1 \
    --from-literal=key2=value2
```

##### 从文件创建
如果配置信息存储在文件中，可以这样创建：
```bash
kubectl create configmap <configmap-name> \
    --from-file=path/to/config/file1 \
    --from-file=path/to/config/file2
```

##### 从目录创建
如果配置信息存储在目录中，可以这样创建：
```bash
kubectl create configmap <configmap-name> \
    --from-file=path/to/config/directory
```

##### yaml定义
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap
data:
  application.properties: |
    property1=value1
    property2=value2
```
然后使用 kubectl apply -f configmap.yaml 命令创建










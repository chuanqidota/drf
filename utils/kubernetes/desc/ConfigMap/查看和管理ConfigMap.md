##### 查看和管理 ConfigMap
* 查看 ConfigMap：`kubectl get configmaps [configmap-name]`
* 获取 ConfigMap 内容：`kubectl describe configmaps [configmap-name]`
* 更新 ConfigMap：修改 YAML 文件后重新应用，或使用 `kubectl edit configmap [configmap-name]` 直接编辑。
* 删除 ConfigMap：`kubectl delete configmap [configmap-name]`
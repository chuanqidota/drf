### 查询回滚历史
```
kubectl rollout history deployment nginx-deployment

>输出
deployments "nginx-deployment"
REVISION    CHANGE-CAUSE
1           kubectl apply --filename=https://k8s.io/examples/controllers/nginx-deployment.yaml --record=true
2           kubectl set image deployment.v1.apps/nginx-deployment nginx=nginx:1.9.1 --record=true
3           kubectl set image deployment.v1.apps/nginx-deployment nginx=nginx:1.91 --record=true
```

### 查看revision详情 版本详情
```
kubectl rollout history deployment nginx-deployment --revision=2

>输出
deployments "nginx-deployment" revision 2
  Labels:       app=nginx
          pod-template-hash=1159050644
  Annotations:  kubernetes.io/change-cause=kubectl set image deployment.v1.apps/nginx-deployment nginx=nginx:1.9.1 --record=true
  Containers:
  nginx:
    Image:      nginx:1.9.1
    Port:       80/TCP
    QoS Tier:
        cpu:      BestEffort
        memory:   BestEffort
    Environment Variables:      <none>
  No volumes.
```

### 回滚到上一个版本
```
kubectl rollout undo deployment nginx-deployment

>输出
deployment.apps/nginx-deployment
```

### 回滚到指定版本
```
kubectl rollout undo deployment nginx-deployment --to-revision=2

>输出
deployment.apps/nginx-deployment
```

### 回滚之前的暂停，Deployment 的更新，以避免新的变更影响回滚操作
```
kubectl rollout pause deployment nginx-deployment
```

### 恢复更新
```
kubectl rollout resume deployment nginx-deployment
```




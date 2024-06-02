### 更新deployment
```
kubectl edit deployment nginx-deployment
```

### 查看发布更新（rollout）的状态
```
kubectl rollout status deployment nginx-deployment

>输出
Waiting for rollout to finish: 2 out of 3 new replicas have been updated...
或者
deployment.apps/nginx-deployment successfully rolled out
```


















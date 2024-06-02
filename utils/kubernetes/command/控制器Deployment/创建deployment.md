### 创建
```
kubectl apply -f https://k8s.io/examples/controllers/nginx-deployment.yaml
```

### 查看
```
kubectl get deployments


> 输出
NAME               DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3         0         0            0           1s
```

### 查看发布状态
```
kubectl rollout status deployment nginx-deployment

> 输出
Waiting for rollout to finish: 2 out of 3 new replicas have been updated...
deployment.apps/nginx-deployment successfully rolled out
```



### 查看该 Deployment 创建的 ReplicaSet（rs）
```
kubectl get rs

> 输出
NAME                          DESIRED   CURRENT   READY   AGE
nginx-deployment-75675f5897   3         3         3       18s
```


### 查看 Pod 的标签
```
kubectl get pods --show-labels

> 输出
NAME                                READY     STATUS    RESTARTS   AGE       LABELS
nginx-deployment-75675f5897-7ci7o   1/1       Running   0          18s       app=nginx,pod-template-hash=3123191453
nginx-deployment-75675f5897-kzszj   1/1       Running   0          18s       app=nginx,pod-template-hash=3123191453
nginx-deployment-75675f5897-qqcnn   1/1       Running   0          18s       app=nginx,pod-template-hash=3123191453
```








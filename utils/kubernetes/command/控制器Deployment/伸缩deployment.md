### 执行伸缩
```
kubectl scale deployment nginx-deployment --replicas=10
```

### 自动伸缩
```
kubectl autoscale deployment nginx-deployment --min=10 --max=15 --cpu-percent=80
```


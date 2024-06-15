#### 查看 Secret
```shell
# 列出所有 Secrets
kubectl get secrets

# 查看 Secret 的详细信息
kubectl describe secret <secret-name>
```

> TIP \
> 默认情况下，kubectl get 和 kubectl describe 命令都避免展示 Secret 的内容。这种做法可以避免密码被偷窥，或者被存储到终端的日志中
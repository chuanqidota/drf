* 下面例子中的 CronJob 每分钟，打印一次当前时间并输出 hello world 信息
```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            args:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure
```
### 创建CronJob
```shell
kubectl create -f https://kuboard.cn/statics/learning/job/cronjob.yaml

>输出
cronjob.batch/hello created
```

### 查看CronJob
```shell
kubectl get cronjob hello

>输出
NAME    SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
hello   */1 * * * *   False     0        <none>          10s
```

### 删除CronJob
```shell
kubectl delete cronjob hello

# 或者

kubectl delete -f https://kuboard.cn/statics/learning/job/cronjob.yaml

```

#### 解码secret
Secret 中的信息可以通过 kubectl get secret 命令获取。例如，执行命令 kubectl get secret mysecret -o yaml 可获取前面章节中所创建的 Secret，输出信息如下
```yaml
apiVersion: v1
kind: Secret
metadata:
  creationTimestamp: 2016-01-22T18:41:56Z
  name: mysecret
  namespace: default
  resourceVersion: "164619"
  uid: cfee02d6-c137-11e5-8d73-42010af00002
type: Opaque
data:
  username: YWRtaW4=
  password: MWYyZDFlMmU2N2Rm
```

执行命令 `echo 'MWYyZDFlMmU2N2Rm' | base64 --decode` 可解码密码字段，输出结果如下：
```text
1f2d1e2e67df
```


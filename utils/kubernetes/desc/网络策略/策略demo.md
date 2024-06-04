> 一个 NetworkPolicy 的 Example 如下所示
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except:
        - 172.17.1.0/24
    - namespaceSelector:
        matchLabels:
          project: myproject
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 6379
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 5978
```
> `ingress`： ingress 是一个数组，代表入方向的白名单规则。每一条规则都将允许与 from 和 ports 匹配的入方向的网络流量发生。例子中的 ingress 包含了一条规则，允许的入方向网络流量必须符合如下条件：
* 请求方可以是如下三种来源当中的任意一种：
* `ipBlock` 为 172.17.0.0/16 网段（请参考 CIDR），但是不包括 172.17.1.0/24 网段
* `namespaceSelector` 标签选择器，匹配标签为 project=myproject
* `podSelector` 标签选择器，匹配标签为 role=frontend

> egress： egress 是一个数组，代表出方向的白名单规则。每一条规则都将允许与 to 和 ports 匹配的出方向的网络流量发生。例子中的 egress 允许的出方向网络流量必须符合如下条件：
* 目标端口为 5978
* 目标 ipBlock 为 10.0.0.0/24 网段（请参考 CIDR）
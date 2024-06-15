#### 从文件创建

* 如果你有包含敏感数据的文件（如用户名和密码），可以使用以下命令创建 Secret

```yaml
kubectl create Secret generic <Secret-name> \
--from-file=./username.txt \
--from-file=./password.txt
```
例如，您的应用程序需要读取如下配置文件内容
```text
apiUrl: "https://my.api.com/api/v1"
username: user
password: password
```
您可以使用下面的 secret.yaml 创建 Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
stringData:
  config.yaml: |-
    apiUrl: "https://my.api.com/api/v1"
    username: user
    password: password
```
执行命令 `kubectl apply -f ./secret.yaml` 输出结果如下所示
```text
secret "mysecret" created
```
执行命令 kubectl get -f ./secret.yaml -o yaml 输出结果如下所示
```yaml
apiVersion: v1
kind: Secret
metadata:
  creationTimestamp: 2018-11-15T20:40:59Z
  name: mysecret
  namespace: default
  resourceVersion: "7225"
  uid: c280ad2e-e916-11e8-98f2-025000000001
type: Opaque
data:
  config.yaml: YXBpVXJsOiAiaHR0cHM6Ly9teS5hcGkuY29tL2FwaS92MSIKdXNlcm5hbWU6IHt7dXNlcm5hbWV9fQpwYXNzd29yZDoge3twYXNzd29yZH19
```


#### 直接命令行创建

* 命令 `kubectl create secret generic db-user-pass –from-literal=username=admin –from-literal=password=1f2d1e2e67df`
* 如果您的密码中包含特殊字符需要转码（例如 $、*、\、!），请使用 \ 进行转码。例如：实际密码为 S!B\*d$zDsb，kubectl
  命令应该写成 `kubectl create secret generic dev-db-secret –from-literal=username=devuser –from-literal=password=S\!B\\*d\$zDsb`
  。如果通过文件创建（--from-file），则无需对文件中的密码进行转码

#### 通过yaml定义

* data：使用 data 字段时，取值的内容必须是 base64 编码的
* stringData：使用 stringData 时，更为方便，您可以直接将取值以明文的方式写在 yaml 文件中

##### 在yaml中定义data

* 假设您要保存 username=admin 和 password=1f2d1e2e67df 到 Secret 中，请先将数据的值转化为 base64 编码，执行如下命令

```shell
echo -n 'admin' | base64
YWRtaW4=
echo -n '1f2d1e2e67df' | base64
MWYyZDFlMmU2N2Rm
```

* 创建 secret.yaml 文件，内容如下所示

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: YWRtaW4=    # "admin" base64 YWRtaW4=
  password: MWYyZDFlMmU2N2Rm

```

* 然后使用 `kubectl apply -f secret.yaml` 命令创建

##### 在yaml中定义stringData

* 有时，您并不想先将用户名和密码转换为 base64 编码之后再创建 Secret，则，您可以通过定义 stringData 来达成，此时 stringData
  中的取值部分将被 apiserver 自动进行 base64 编码之后再保存

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
stringData:
  username: admin
  password: 1f2d1e2e67df
```



  # 基于 Django & DRF 的 DevOps 模板

  这是一个基于 Django REST Framework（DRF）构建的 Django 项目模板（Django 5.0.4 + DRF 3.15.1），
  内置了常用的 DevOps 模块与工具集成，提供 MySQL、Redis、Elasticsearch、Celery 等开箱即用的配置，
  帮助开发者快速搭建可扩展、易维护的后端应用。

  ## 功能特性

  ### 通用 Django 配置
  - **数据库配置**：默认使用 MySQL（pymysql，utf8mb4、严格事务模式），PostgreSQL 可按需自行扩展。
  - **安全配置**：内置 CSRF、XSS 防护与 CORS 跨域配置（django-cors-headers），支持反向代理场景下的 SSL 头透传。
  - **日志系统**：控制台 + 文件双通道日志，支持多级别与文件轮转（输出至 `logs/drf/drf.log`）。
  - **缓存**：基于 django-redis 的缓存支持，用于性能优化。
  - **国际化**：默认中文（zh-Hans）与时区（Asia/Shanghai），支持多语言。
  - **Celery & Beat**：基于 Redis 的任务队列，集成 django-celery-results（结果入库）与 django-celery-beat（数据库调度器）。
  - **Gunicorn 配置**：生产级配置（`drf/gunicorn.py`，worker 数随 CPU 自动伸缩、max_requests 防内存泄漏）。

  ### 内置模块
  - **加密模块**：内置 Fernet 对称加密，用于安全存储敏感数据（如用户口令加密存储）；另提供 RSA 加解密与签名工具。
  - **全局异常处理**：统一 DRF 异常响应格式（message / code / status），保证接口报错风格一致。
  - **审计中间件**：自动记录每个请求的用户、IP、方法、参数到 Elasticsearch 审计索引（按年分索引），并提供审计日志查询接口。
  - **Excel 导出**：ViewSet 集成 `?export=true` 即可将列表数据导出为 xlsx（openpyxl）。
  - **权限管理**：内置 `IsValidUser` / `IsAdminUser` 权限类，对用户角色与权限做细粒度控制。
  - **Swagger 文档**：基于 drf-yasg 自动生成 API 文档，提供 Swagger UI 与 ReDoc 页面。
  - **登录与用户模块**：自定义用户模型（部门树、角色、账号类型等），同时启用 Session、Token、JWT（SimpleJWT）三种认证方式。（OAuth2 暂未实现）
  - **任务模块**：提供 Celery 周期任务（PeriodicTask）与 Crontab 调度表的 CRUD API。（预留：该模块代码尚未注册进 INSTALLED_APPS，路由未挂载）
  - **限流**：（预留，尚未实现：`common/throttle/` 目前为空，未做任何限流配置）

  ### DevOps 工具集成
  本模板还封装了各类常用 DevOps 工具与系统（位于 `utils/` 目录）：

  - **Ansible**：双封装（Ansible Python API 与 ansible-runner），用于执行 ad-hoc 命令与 playbook，实现部署与配置管理自动化。
  - **Subprocess**：封装 subprocess，用于执行系统命令与自动化运维操作。
  - **配置中心**：
    - **Nacos**：动态配置的获取、监听与回调。
    - **Apollo**：（预留，尚未实现）
    - **Consul**：KV 存储、服务注册/发现、健康检查。
  - **邮件**：基于 smtplib 的发信封装，支持附件与抄送，用于通知与告警。
  - **Elasticsearch（ES）**：两套封装（原生 client 与 elasticsearch-dsl），支持索引管理、文档 CRUD 与检索，用于日志存储与数据分析。
  - **ETCD**：分布式 KV 存储封装（含租约），用于配置管理。
  - **Excel/CSV 处理**：三套封装（openpyxl / 标准库 csv / pandas），实现数据的导出与处理。
  - **GitLab**：基于 python-gitlab 的封装（组、用户、项目的 CRUD），用于版本管理与 CI/CD 集成。
  - **Harbor**：（预留，尚未实现）
  - **Jenkins**：jenkinsapi 与 python-jenkins 双封装，支持 Job 创建/更新/构建、视图管理与参数化构建。
  - **Kafka**：生产者/消费者封装与 Topic 管理，用于大规模消息与事件驱动架构。
  - **日志（Log）**：日志封装（get_logger）与 Kafka 日志处理器（将日志投递到 Kafka 主题），实现集中式日志管理。
  - **MySQL**：pymysql 与 mysqlclient 双封装，用于直连数据库执行查询与维护操作。
  - **Paramiko**：SSH 远程执行命令、文件上传下载，用于远程运维操作。
  - **RabbitMQ**：基于 pika 的封装（exchange/queue 声明绑定、发布、消费），用于后台任务与系统间通信。
  - **Redis**：redis-py 封装（string/hash/list/set/pub-sub），用于缓存、会话存储与消息代理。
  - **RocketMQ**：生产者/消费者封装，用于高性能场景的消息队列。
  - **S3**：基于 boto3 的对象存储封装（兼容任意 S3 端点），用于文件上传、下载与备份。
  - **SaltAPI**：SaltStack REST API 客户端（命令执行、事件轮询、minion 管理），用于基础设施管理自动化。
  - **Sentry**：（预留，尚未实现）
  - **TextFSM**：内置华为等网络设备配置解析模板（.textfsm），用于网络设备回显的结构化解析。（暂未包含调用代码）
  - **Kubernetes**：client 封装（namespace/deployment/service/pod/日志/密钥管理、伸缩与重启）及跨集群资源迁移脚本。
  - **Neo4j**：图数据库驱动封装、LangChain 自然语言问答（GraphCypherQAChain）与 neomodel 图模型。
  - **Fabric**：基于 Fabric 的远程命令执行（含 sudo）与文件上传下载。
  - **FastDFS**：分布式文件系统封装，用于文件上传、下载与删除。
  - **DeepSeek**：基于 OpenAI SDK 的 DeepSeek 对话客户端（含流式输出示例）。
  - **定时任务工具**：croniter（cron 表达式解析）与 schedule（轻量定时调度）封装。
  - **其他工具**：YAML 转换工具、函数耗时统计装饰器、协程/进程/线程并发示例集。

  ## 环境依赖
  - Django REST Framework
  - MySQL（默认数据库）
  - Redis（缓存与 Celery broker）
  - Celery 与 Beat（后台任务与周期调度）
  - Docker（可选，用于容器化部署）
  - Gunicorn（生产部署）

  > 注：`requirements.txt` 已包含主要依赖；部分工具模块引用的库（如 nacos、langchain、neomodel、PyJWT）未列入其中，使用对应模块时需自行安装。

  ## 使用场景

  部署完成后，可将预配置模块用于以下 DevOps 相关场景：

  - **自动化部署**：结合 Ansible、Jenkins 或 GitLab 实现持续交付（`deploy/` 目录内置 supervisor + nginx 的部署配置，涵盖 gunicorn、celery worker、beat、flower 及进程监控）。
  - **服务发现与配置**：接入 Nacos、Apollo 或 Consul 实现微服务的配置管理与发现。
  - **任务调度**：使用 Celery 与 Beat 调度和运行后台任务，通过 Flower 观察任务执行情况。
  - **API 文档**：通过 Swagger（/api/swagger/）自动生成并查看接口文档。
  - **错误追踪**：（预留：Sentry 集成尚未实现）

  ## 参与贡献

  欢迎 fork 本项目、提交 Issue 和 Pull Request，随时期待你的贡献！

  ## 许可证

  本项目基于 MIT 许可证开源（仓库中暂未包含 LICENSE 文件）。

# pip install neomodel


import datetime

from neomodel import StructuredNode, UniqueIdProperty, StructuredRel, StringProperty, RelationshipTo, \
    config, DateTimeNeo4jFormatProperty


class BaseNode(StructuredNode):
    """
    抽象节点基类
    """
    __abstract_node__ = True

    uid = UniqueIdProperty()
    created_at = DateTimeNeo4jFormatProperty(default_now=True)
    updated_at = DateTimeNeo4jFormatProperty(default_now=True)

    def save(self):
        self.updated_at = datetime.datetime.now()
        return super().save()


class BaseRelation(StructuredRel):
    """
    抽象关系基类
    """
    __abstract_rel__ = True

    created_at = DateTimeNeo4jFormatProperty(default_now=True)
    updated_at = DateTimeNeo4jFormatProperty(default_now=True)

    def save(self):
        self.updated_at = datetime.datetime.now()
        return super().save()


class ContainsRel(BaseRelation):
    """
    包含关系
    """
    remark = StringProperty()


class BelongsToRel(BaseRelation):
    """
    属于关系
    """
    remark = StringProperty()


class Tenant(BaseNode):
    __label__ = "Tenant"

    name = StringProperty(required=True)
    alias = StringProperty()
    key = StringProperty(required=True, unique_index=True)

    # 租户包含
    users = RelationshipTo("User", "CONTAINS", model=ContainsRel)
    roles = RelationshipTo("Role", "CONTAINS", model=ContainsRel)
    apis = RelationshipTo("API", "CONTAINS", model=ContainsRel)


class User(BaseNode):
    __label__ = "User"

    cn_name = StringProperty(required=True)
    en_name = StringProperty(required=True, unique_index=True)
    email = StringProperty()

    # 用户属于角色
    roles = RelationshipTo("Role", "BELONGS_TO", model=BelongsToRel)


class Role(BaseNode):
    __label__ = "Role"

    cn_name = StringProperty(required=True)
    en_name = StringProperty(required=True, unique_index=True)

    # 角色包含 API
    apis = RelationshipTo("API", "CONTAINS", model=ContainsRel)


class API(BaseNode):
    __label__ = "API"

    METHOD_CHOICES = {"GET": "GET", "POST": "POST", "DELETE": "DELETE", "PATCH": "PATCH", "PUT": "PUT"}

    path = StringProperty(required=True)
    method = StringProperty(required=True, choices=METHOD_CHOICES)
    name = StringProperty(required=True)


if __name__ == '__main__':
    """
    NEO4J_URI=neo4j+s://0143b13f.databases.neo4j.io
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=PiZUB3SIcbPB5s3ok5AU9mMn6QWHfVzOlkD2d-pyu4Q
    NEO4J_DATABASE=neo4j
    AURA_INSTANCEID=0143b13f
    AURA_INSTANCENAME=Instance01
    """
    config.DATABASE_URL = 'neo4j+s://neo4j:PiZUB3SIcbPB5s3ok5AU9mMn6QWHfVzOlkD2d-pyu4Q@0143b13f.databases.neo4j.io'

    ## 初始化数据
    """
    
    # ========== 清理旧数据（可选） ==========
    from neomodel import db
    db.cypher_query("MATCH (n) DETACH DELETE n")

    print("已清空旧数据")

    # ========== 创建租户 ==========
    tenant1 = Tenant(name="租户A", alias="tenant-a", key="tenant_a").save()
    tenant2 = Tenant(name="租户B", alias="tenant-b", key="tenant_b").save()

    print("创建租户完成")

    # ========== 创建用户 ==========
    u1 = User(cn_name="张三", en_name="zhangsan", email="zhangsan@test.com").save()
    u2 = User(cn_name="李四", en_name="lisi", email="lisi@test.com").save()
    u3 = User(cn_name="王五", en_name="wangwu", email="wangwu@test.com").save()

    print("创建用户完成")

    # ========== 创建角色 ==========
    admin_role = Role(cn_name="管理员", en_name="admin").save()
    dev_role = Role(cn_name="开发", en_name="developer").save()
    viewer_role = Role(cn_name="只读", en_name="viewer").save()

    print("创建角色完成")

    # ========== 创建 API ==========
    api_list_user = API(path="/api/user/list", method="GET", name="用户列表").save()
    api_create_user = API(path="/api/user/create", method="POST", name="创建用户").save()
    api_delete_user = API(path="/api/user/delete", method="DELETE", name="删除用户").save()

    print("创建API完成")

    # ========== 建立租户包含关系 ==========
    tenant1.users.connect(u1)
    tenant1.users.connect(u2)
    tenant1.roles.connect(admin_role)
    tenant1.roles.connect(dev_role)
    tenant1.apis.connect(api_list_user)
    tenant1.apis.connect(api_create_user)
    tenant1.apis.connect(api_delete_user)

    tenant2.users.connect(u3)
    tenant2.roles.connect(viewer_role)
    tenant2.apis.connect(api_list_user)

    print("建立租户关系完成")

    # ========== 建立用户角色关系 ==========
    u1.roles.connect(admin_role, {"remark": "主管理员"})
    u2.roles.connect(dev_role, {"remark": "开发人员"})
    u3.roles.connect(viewer_role, {"remark": "只读用户"})

    print("建立用户角色关系完成")

    # ========== 建立角色 API 权限 ==========
    admin_role.apis.connect(api_list_user)
    admin_role.apis.connect(api_create_user)
    admin_role.apis.connect(api_delete_user)

    dev_role.apis.connect(api_list_user)
    dev_role.apis.connect(api_create_user)

    viewer_role.apis.connect(api_list_user)

    print("建立角色权限关系完成")
    """

    # 人员租户-角色-api
    t = Tenant.nodes.get(name="租户A")
    user = t.users.get(en_name="zhangsan")
    result = []
    for role in user.roles:
        for api in role.apis:
            result.append({"method": api.method, "path": api.path, "name": api.name})
    print(result)

    # user = User.nodes.get(en_name="zhangsan")
    # apis = set()
    # for role in user.roles:
    #     for api in role.apis:
    #         apis.add((api.method, api.path))
    # print(apis)


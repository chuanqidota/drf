from neo4j import GraphDatabase

from neo4j.exceptions import Neo4jError


# pip install neo4j

class Neo4jConnection:
    """
        neo4j连接
    """

    def __init__(self, uri, user, password, database="neo4j", max_connection_pool_size=50, connection_timeout=30):
        self.driver = GraphDatabase.driver(uri,
                                           auth=(user, password),
                                           max_connection_pool_size=max_connection_pool_size,
                                           connection_timeout=connection_timeout)
        self.database = database

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.driver:
            self.driver.close()

    @staticmethod
    def _run_read(tx, query, parameters):
        result = tx.run(query, **parameters)
        return [record.data() for record in result]

    @staticmethod
    def _run_write(tx, query, parameters):
        result = tx.run(query, **parameters)
        return [record.data() for record in result]

    def execute_read(self, query, **parameters):
        try:
            with self.driver.session(database=self.database) as session:
                return session.execute_read(self._run_read, query, parameters)
        except Neo4jError as e:
            raise RuntimeError(f"Neo4j Read Error: {e}")

    def execute_write(self, query, **parameters):
        try:
            with self.driver.session(database=self.database) as session:
                return session.execute_write(self._run_write, query, parameters)
        except Neo4jError as e:
            raise RuntimeError(f"Neo4j Write Error: {e}")


if __name__ == "__main__":
    """
    # Wait 60 seconds before connecting using these details, or login to https://console.neo4j.io to validate the Aura Instance is available
    NEO4J_URI=neo4j+s://0143b13f.databases.neo4j.io
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=PiZUB3SIcbPB5s3ok5AU9mMn6QWHfVzOlkD2d-pyu4Q
    NEO4J_DATABASE=neo4j
    AURA_INSTANCEID=0143b13f
    AURA_INSTANCENAME=Instance01
    """
    # 连接数据库
    _uri = "neo4j+s://0143b13f.databases.neo4j.io"
    _username = "neo4j"
    _password = "PiZUB3SIcbPB5s3ok5AU9mMn6QWHfVzOlkD2d-pyu4Q"
    conn = Neo4jConnection(_uri, _username, _password)

    # 创建节点
    create_query = """
    CREATE (u:User {
        name: $name,
        age: $age,
        created_at: datetime()
    })
    RETURN id(u) AS id, u
    """
    result = conn.execute_write(
        create_query,
        name="Alice",
        age=30
    )
    print(result)

    # 查询节点-查询全部
    query = """
    MATCH (u:User)
    RETURN id(u) AS id, u.name AS name, u.age AS age
    """
    result = conn.execute_read(query)
    print(result)

    # 查询节点-按条件查询
    query = """
    MATCH (u:User {name: $name})
    RETURN id(u) AS id, u
    """

    result = conn.execute_read(query, name="Alice")
    print(result)

    # 查询节点-分页查询
    query = """
    MATCH (u:User)
    RETURN u
    SKIP $skip LIMIT $limit
    """

    result = conn.execute_read(query, skip=0, limit=10)
    print(result)

    # 更新节点
    update_query = """
    MATCH (u:User)
    WHERE id(u) = $id
    SET u.age = $age,
        u.updated_at = datetime()
    RETURN u
    """

    result = conn.execute_write(
        update_query,
        id=123,
        age=35
    )
    print(result)

    # 删除节点-普通删除(无关系)
    delete_query = """
    MATCH (u:User)
    WHERE id(u) = $id
    DELETE u
    """

    conn.execute_write(delete_query, id=123)

    # 删除节点-强制删除(含关系)
    delete_query = """
    MATCH (u:User)
    WHERE id(u) = $id
    DETACH DELETE u
    """

    conn.execute_write(delete_query, id=123)

    # 关系操作-创建关系
    create_rel_query = """
    MATCH (a:User), (b:User)
    WHERE id(a) = $from_id AND id(b) = $to_id
    CREATE (a)-[r:FRIEND {
        since: $since
    }]->(b)
    RETURN id(r) AS rel_id
    """

    result = conn.execute_write(
        create_rel_query,
        from_id=1,
        to_id=2,
        since="2024"
    )

    print(result)

    # 关系操作-查询某人的好友
    query = """
    MATCH (a:User)-[r:FRIEND]->(b:User)
    WHERE id(a) = $id
    RETURN id(r) AS rel_id, b.name AS friend_name, r.since AS since
    """

    result = conn.execute_read(query, id=1)
    print(result)

    # 关系操作-查询双向关系
    query = """
    MATCH (a:User)-[r:FRIEND]-(b:User)
    WHERE id(a) = $id
    RETURN b, r
    """

    result = conn.execute_read(query, id=1)
    print(result)

    # 关系操作-更新关系属性
    update_rel_query = """
    MATCH ()-[r:FRIEND]->()
    WHERE id(r) = $rel_id
    SET r.since = $since,
        r.updated_at = datetime()
    RETURN r
    """

    conn.execute_write(update_rel_query, rel_id=10, since="2025")

    # 关系操作-删除关系
    delete_rel_query = """
    MATCH ()-[r:FRIEND]->()
    WHERE id(r) = $rel_id
    DELETE r
    """

    conn.execute_write(delete_rel_query, rel_id=10)

    # 查询路径
    query = """
    MATCH p = (a:User)-[:FRIEND*1..3]->(b:User)
    WHERE id(a) = $id
    RETURN p
    """

    result = conn.execute_read(query, id=1)

    print(result)

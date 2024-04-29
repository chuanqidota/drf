import pymysql


class PyMysqlManager:
    def __init__(self, host='localhost', user='root', password='', database='', port=3306, charset='utf8mb4'):
        """
        初始化数据库连接配置
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.charset = charset
        self.connection = None

    def connect(self):
        """
        连接到MySQL数据库
        """
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset=self.charset
            )
            print("Connected to the MySQL server successfully.")
        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")

    def disconnect(self):
        """
        关闭数据库连接
        """
        if self.connection:
            self.connection.close()
            print("MySQL connection is closed.")

    def execute_query(self, query, params=None):
        """
        执行SQL查询并返回结果集
        """
        with self.connection.cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                column_names = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    row_dict = dict(zip(column_names, row))
                    results.append(row_dict)
                return results
            except pymysql.MySQLError as e:
                print(f"Error executing query: {e}")
                return None

    def execute_nonquery(self, query, params=None):
        """
        执行非查询操作（如INSERT, UPDATE, DELETE）
        """
        with self.connection.cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                return cursor.rowcount
            except pymysql.MySQLError as e:
                print(f"Error executing non-query: {e}")
                self.connection.rollback()
                return None


# 使用示例
if __name__ == "__main__":
    db = PyMysqlManager(host='127.0.0.1', user='root', password='jinang123', database='rbac')
    try:
        db.connect()
        # 执行查询
        # query = "SELECT * FROM dept"
        # print(db.execute_query(query))

        # 执行非查询操作
        non_query = "INSERT INTO dept (name, pid) VALUES (%s, %s)"
        _params = ('开发部', "2")
        print(db.execute_nonquery(non_query, _params))
    except Exception as e:
        print(e)
    finally:
        db.disconnect()

import MySQLdb

"""
mysqlclient==2.0.3
"""


class MysqlClientManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print("Connected to MySQL database")
        except MySQLdb.Error as e:
            print(f"Error connecting to MySQL: {e}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("MySQL connection is closed")

    def execute_query(self, query, params=None):
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
            except MySQLdb.Error as e:
                print(f"Error executing query: {e}")
                return None

    def execute_noquery(self, query, params=None):
        with self.connection.cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                return cursor.rowcount  # For queries that don't return rowcount
            except MySQLdb.Error as e:
                print(f"Error executing non-query: {e}")
                self.connection.rollback()
                return False


if __name__ == '__main__':
    manager = MysqlClientManager(host='localhost', user='root', password='jinang123', database='rbac')
    try:
        manager.connect()
        # 执行查询
        query = "SELECT * FROM dept"
        print(manager.execute_query(query))
        # 执行非查询操作
        # non_query = "INSERT INTO dept (name, pid) VALUES (%s, %s)"
        # _params = ('开发部', "2")
        # print(manager.execute_noquery(non_query, _params))
    except Exception as e:
        print(e)
    finally:
        manager.disconnect()

from elasticsearch import Elasticsearch

"""
主要是针对es6用

pip install elasticsearch==6.8.2
【完美解决】Python报错：NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the ‘ssl‘ modul
参考：https://blog.csdn.net/gxhuhuhu/article/details/136156085
pip uninstall urllib3
pip install urllib3==1.26.15
"""


class ElasticsearchClient:
    def __init__(self, hosts, verify_certs=False, use_ssl=False, sniff_on_start=True, sniff_on_connection_fail=True,
                 sniffer_timeout=30):
        """
        初始化Elasticsearch客户端。

        :param hosts:
            [
                'http://user:secret@localhost:9200/',
                'https://user:secret@other_host:443/production' # 这里是带用户名和密码
            ]
        """
        self.es = Elasticsearch(hosts=hosts,
                                verify_certs=verify_certs,
                                use_ssl=use_ssl,
                                sniff_on_start=sniff_on_start,  # 启动时嗅探集群状态
                                sniff_on_connection_fail=sniff_on_connection_fail,  # 连接失败时重新嗅探
                                sniffer_timeout=sniffer_timeout,  # 嗅探超时时间
                                )

    def create_index(self, index, mappings=None):
        """
        创建索引。

        :param index: 索引名称。
        :param mappings: 映射定义，字典形式。
            {
                "field1": {
                    "type": "text"
                },
                "field2": {
                    "type": "integer"
                },
                "field3": {
                    "type": "date"
                },
                "field4": {
                    "type": "keyword"
                }
            }
        """

        try:
            if not self.es.indices.exists(index=index):
                if mappings:
                    self.es.indices.create(index=index, body={"mappings": {"properties": mappings}}, ignore=400)
                else:
                    self.es.indices.create(index=index)
            return True
        except Exception as e:
            print(f"创建索引-{index}-失败-{repr(e)}")
            return False

    def delete_index(self, index):
        """
        删除索引。

        :param index: 索引名称。
        """
        try:
            self.es.indices.delete(index=index)
            return True
        except Exception as e:
            print(f"删除索引-{index}-失败-{repr(e)}")
            return False

    def put_mapping(self, index, properties):
        """
        更新或创建索引的映射信息。

        :param index: 索引名称。
        :param properties: 映射属性，字典形式，定义字段类型和属性。
        """
        body = {"properties": properties}
        try:
            self.es.indices.put_mapping(index=index, body=body)
            return True
        except Exception as e:
            print(f"更新索引-{index}-的属性失败-{repr(e)}")

    def get_mapping(self, index):
        """
        获取索引的映射信息。

        :param index: 索引名称。
        :return: 索引的映射信息，如果索引存在的话。
        """
        try:
            res = self.es.indices.get_mapping(index=index)
            return res[index]['mappings']
        except Exception as e:
            print(f"获取索引-{index}-的mapping信息失败-{repr(e)}")
            return None

    def insert_document(self, index, body, doc_type):
        """
        索引文档。

        :param index: 索引名称。
        :param body: 文档内容，字典形式。
        :param doc_type: 文档类型，后续已经去除。
        """
        res = self.es.index(index=index, body=body, doc_type=doc_type)
        return res

    def delete_by_query(self, index, query):
        """
        根据查询条件批量删除文档。

        :param index: 索引名称。
        :param query: 查询条件，用于指定要删除的文档，字典形式。
        """
        try:
            response = self.es.delete_by_query(index=index, body=query)
            return response['deleted']
        except Exception as e:
            print(f"更具查询条件删除失败-{repr(e)}")
            return 0

    def search(self, index, query):
        """
        执行搜索。

        :param index: 索引名称。
        :param query: 查询DSL，字典形式。
        :return: 搜索结果。
        """
        res = self.es.search(index=index, body=query)
        return res['hits']['hits']


# 使用示例
if __name__ == "__main__":
    hosts = ["http://127.0.0.1:9200"]
    client = ElasticsearchClient(hosts)

    # 创建索引
    _index = "test042910"
    # _mappings = {
    #     "field1": {
    #         "type": "text"
    #     },
    #     "field2": {
    #         "type": "integer"
    #     },
    #     "field3": {
    #         "type": "date"
    #     },
    #     "field4": {
    #         "type": "keyword"
    #     }
    # }
    # print(client.create_index(_index, _mappings))

    # 更改maping
    # _properties = {
    #     "filed5": {
    #         "type": "keyword"
    #     }
    # }
    # print(client.put_mapping(_index, _properties))

    # 获取索引信息
    # print(client.get_mapping(_index))

    import datetime

    # 插入数据
    # _body = {
    #     "field1": "field1_text",
    #     "field2": 2,
    #     "field3": datetime.datetime.now().strftime("%Y-%m-%d"),
    #     "field4": "field4_keyword",
    #     "filed5": "filed5_keyword"
    # }
    # _doc_type = "my_doc_type"
    # print(client.insert_document(_index, _body, _doc_type))

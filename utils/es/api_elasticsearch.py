from elasticsearch import Elasticsearch, NotFoundError


class ElasticsearchClient:
    def __init__(self, hosts=["localhost"], http_auth=None, timeout=30):
        """
        初始化Elasticsearch客户端。

        :param hosts: Elasticsearch服务器地址列表，默认为localhost。
        :param http_auth: HTTP认证信息，例如('username', 'password')。
        :param timeout: 请求超时时间，单位秒。
        """
        self.es = Elasticsearch(hosts=hosts, http_auth=http_auth, timeout=timeout)

    def create_index(self, index_name, mappings=None):
        """
        创建索引。

        :param index_name: 索引名称。
        :param mappings: 映射定义，字典形式。
        """
        if not self.es.indices.exists(index=index_name):
            if mappings:
                self.es.indices.create(index=index_name, body={"mappings": mappings})
            else:
                self.es.indices.create(index=index_name)
            print(f"Index '{index_name}' created.")
        else:
            print(f"Index '{index_name}' already exists.")

    def delete_index(self, index_name):
        """
        删除索引。

        :param index_name: 索引名称。
        """
        try:
            self.es.indices.delete(index=index_name)
            print(f"Index '{index_name}' deleted.")
        except NotFoundError:
            print(f"Index '{index_name}' does not exist.")

    def get_mapping(self, index_name):
        """
        获取索引的映射信息。

        :param index_name: 索引名称。
        :return: 索引的映射信息，如果索引存在的话。
        """
        try:
            res = self.es.indices.get_mapping(index=index_name)
            return res[index_name]['mappings']
        except NotFoundError:
            print(f"Index '{index_name}' not found.")
            return None

    def put_mapping(self, index_name, properties):
        """
        更新或创建索引的映射信息。

        :param index_name: 索引名称。
        :param properties: 映射属性，字典形式，定义字段类型和属性。
        """
        body = {"properties": properties}
        try:
            self.es.indices.put_mapping(index=index_name, body=body)
            print(f"Mapping updated for index '{index_name}'.")
        except Exception as e:
            print(f"Failed to update mapping for index '{index_name}': {e}")

    def create_index_with_mapping(self, index_name, mappings):
        """
        创建索引并同时指定映射信息。

        :param index_name: 索引名称。
        :param mappings: 映射定义，字典形式。
        """
        self.create_index(index_name, mappings=mappings)

    def index_document(self, index_name, doc_id, document):
        """
        索引文档。

        :param index_name: 索引名称。
        :param doc_id: 文档ID。
        :param document: 文档内容，字典形式。
        """
        res = self.es.index(index=index_name, id=doc_id, body=document)
        print(f"Indexed document '{doc_id}': {res['result']}")

    def get_document(self, index_name, doc_id):
        """
        获取文档。

        :param index_name: 索引名称。
        :param doc_id: 文档ID。
        :return: 文档内容，如果存在的话。
        """
        try:
            res = self.es.get(index=index_name, id=doc_id)
            return res['_source']
        except NotFoundError:
            print(f"Document '{doc_id}' not found in index '{index_name}'.")
            return None

    def delete_by_query(self, index_name, query):
        """
        根据查询条件批量删除文档。

        :param index_name: 索引名称。
        :param query: 查询条件，用于指定要删除的文档，字典形式。
        """
        try:
            response = self.es.delete_by_query(index=index_name, body=query)
            print(f"Deleted {response['deleted']} documents matching the query.")
        except Exception as e:
            print(f"An error occurred while deleting documents: {e}")

    def search(self, index_name, query):
        """
        执行搜索。

        :param index_name: 索引名称。
        :param query: 查询DSL，字典形式。
        :return: 搜索结果。
        """
        res = self.es.search(index=index_name, body=query)
        return res['hits']['hits']


# 使用示例
if __name__ == "__main__":
    client = ElasticsearchClient()
    index_name = "test_index"

    # 创建索引
    client.create_index(index_name)

    # 索引文档
    doc_id = 1
    document = {"title": "Test Document", "content": "This is a test document."}
    client.index_document(index_name, doc_id, document)

    mapping_example = {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"},
            "publish_date": {"type": "date"},
            "is_published": {"type": "boolean"}
        }
    }

    # 创建索引并指定映射
    client.create_index_with_mapping("test_index_mapped", mapping_example)

    # 获取并打印映射信息
    mapping_info = client.get_mapping("test_index_mapped")
    print("Mapping Information:")
    print(mapping_info)

    # 更新映射（注意：实际中应谨慎操作，可能需要重建索引）
    new_property = {"author": {"type": "keyword"}}
    client.put_mapping("test_index_mapped", new_property)

    # 再次获取映射信息以确认更新
    updated_mapping_info = client.get_mapping("test_index_mapped")
    print("Updated Mapping Information:")
    print(updated_mapping_info)

    # 获取文档
    print(client.get_document(index_name, doc_id))

    # 搜索文档
    query = {"query": {"match_all": {}}}
    results = client.search(index_name, query)
    for hit in results:
        print(hit["_source"])

    # 删除索引（可选）
    # client.delete_index(index_name)

    # 批量删除示例：删除所有is_published为false的文档
    delete_query = {
        "query": {
            "term": {
                "is_published": False
            }
        }
    }
    client.delete_by_query("test_index_mapped", delete_query)

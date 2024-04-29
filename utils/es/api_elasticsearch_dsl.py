import datetime
import traceback

from elasticsearch_dsl.connections import get_connection


class ElasticSearchManager(object):
    """
    ES类封装
    """

    def __init__(self, _client=None):
        """
        初始化函数
        :param _client: Elasticsearch 客户端实例，如果未提供，则从连接池获取一个连接
        :return: 无
        """

        # 判断是否提供了client参数，如果提供则使用，否则从连接池获取一个连接
        self.client = _client if _client else get_connection()
        self.client.options(ignore_status=400)

    def create_index(self, index, mapping=None):
        """
            创建索引

        :param index: 指定的索引名称。
        :param mapping: 
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
        :return: 布尔值，索引成功创建返回True，否则返回False。
        """
        # 检查索引是否已经存在，如果不存在则尝试创建
        if not self.client.indices.exists(index=index):
            try:
                if mapping:
                    response = self.client.indices.create(index=index, body={"mappings": {"properties": mapping}})
                else:
                    response = self.client.indices.create(index=index)
                # 判断索引创建是否成功
                # {'acknowledged': True, 'shards_acknowledged': True, 'index': 'test_index'}
                return True if response["acknowledged"] else False
            except Exception as e:
                print(traceback.format_exc(),repr(e))
                return False
        else:
            return True

    def get_index_info(self, index):
        """
            获取索引信息

        :param index: 指定的索引名称。
        :return: 索引信息，如果索引不存在则返回None。
                 {
                    'test_index': {
                        'aliases': {},
                        'mappings': {},
                        'settings': {
                            'index': {
                                'routing': {
                                    'allocation': {
                                        'include': {
                                            '_tier_preference': 'data_content'
                                        }
                                    }
                                },
                                'number_of_shards': '1',
                                'provided_name': 'test_index',
                                'creation_date': '1712984163600',
                                'number_of_replicas': '1',
                                'uuid': 'uTk-i02TQ9akKG1wIAiuJw',
                                'version': {
                                    'created': '8080199'
                                }
                            }
                        }
                    }
                }
        """
        try:
            response = self.client.indices.get(index=index)
            return response
        except Exception as e:
            # 获取索引信息过程中发生异常，返回None
            return None

    def exist_index(self, index):
        """
        检查索引是否存在

        :param index: 指定的索引名称。
        :return: 布尔值，索引存在返回True，否则返回False。
        """
        return self.client.indices.exists(index=index).body

    def delete_index(self, index):
        """
        删除指定的索引。

        :param index: 索引的名称，必须是一个非空字符串。
        :return: 如果索引成功被删除则返回True，如果索引不存在或删除操作出现异常则返回False。
        """
        try:
            if self.client.indices.exists(index=index):
                self.client.indices.delete(index=index)
                return True
            else:
                return False
        except Exception as e:
            return False

    def get_mapping(self, index):
        """
        获取指定索引的映射信息。

        :param index: 指定的索引名称。
        :return: 映射信息，如果索引不存在则返回None。
                 {
                     "my_index": {
                         "mappings": {
                             "properties": {
                                 "field1": {...},
                                 "field2": {...},
                                 ...
                             }
                         }
                     }
                 }
        """
        try:
            response = self.client.indices.get_mapping(index=index)
            return response
        except Exception as e:
            return None

    def create_or_add_mapping(self, index, mappings):
        """
        向指定索引中设置映射（mapping）索引已经存在
        只能增加不能修改
        :param index: 目标索引名称。
        :param mappings: 映射定义，应为一个字典结构
            {
                 "field1": {
                    "type":"keyword"
                 }
            }
        :return: 如果映射设置成功，返回 True；否则返回 False。
        """
        try:
            response = self.client.indices.put_mapping(index=index, body={"properties": mappings})
            return True if response["acknowledged"] else False
        except Exception as e:
            print(f"Failed to put mappings for index {index}: {e}")
        return False

    def insert_document(self, index, document_data, document_id=None):
        """
        插入一个文档到指定索引。

        :param index: 索引名称。
        :param document_id: 文档ID。
        :param document_data: 文档数据，应为一个字典结构。
             {
                  "field1": "value1",
                  "field2": "value2",
                  ...
            }
        :return: 插入操作是否成功，返回True或False。
        """
        try:
            if document_id:
                self.client.index(index=index, id=document_id, body=document_data)
            else:
                self.client.index(index=index, body=document_data)
            return True
        except Exception as e:
            print(f"Failed to insert document into index {index}: {e}")
            return False

    def insert_timestamp_document(self, index, document_data, document_id=None):
        """
        向指定索引中插入带有时间戳的文档。

        :param index: 文档将要被插入的索引名称。
        :param document_data: 要插入的文档数据，字典格式，其中将包含时间戳。
        :param document_id: (可选)要插入文档的ID。如果未提供，则由系统自动生成。
        :return: 返回插入文档的结果，具体取决于insert_document方法的实现。
        """

        # 为文档数据添加当前时间戳
        document_data.update({"@timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        # 调用方法插入更新后的时间戳文档
        return self.insert_document(index, document_data, document_id)

    def get_document(self, index, document_id):
        """
        获取指定索引中特定ID的文档。

        :param index: 索引名称。
        :param document_id: 文档ID。
        :return: 文档数据（字典形式），如果文档不存在，则返回None。
                  {
                      "field1": "value1",
                      "field2": "value2",
                      ...
                  }
        """
        try:
            response = self.client.get(index=index, id=document_id)
            return response["_source"]
        except Exception as e:
            print(f"Failed to retrieve document from index {index}: {e}")
            return None

    def update_document(self, index, document_id, update_data):
        """
        更新指定索引中特定ID的文档的部分字段。

        :param index: 索引名称。
        :param document_id: 文档ID。
        :param update_data: 待更新的字段及其新值，应为一个字典结构。
             {
                  "field1": "updated_value1",
                  "new_field": "new_value"
            }
        :return: 更新操作是否成功，返回True或False。
        """
        try:
            self.client.update(index=index, id=document_id, body={"doc": update_data})
            return True
        except Exception as e:
            print(f"Failed to update document in index {index}: {e}")
            return False

    def delete_document(self, index, document_id):
        """
        删除指定索引中特定ID的文档。

        :param index: 索引名称。
        :param document_id: 文档ID。
        :return: 删除操作是否成功，返回True或False。
        """
        try:
            self.client.delete(index=index, id=document_id)
            return True
        except Exception as e:
            print(f"Failed to delete document from index {index}: {e}")
            return False

    def delete_documents_by_query(self, index, query):
        """
        根据给定的查询条件，从指定索引中删除匹配的文档。

        :param index: 索引名称。
        :param query: 查询条件，应为一个字典结构，符合Elasticsearch查询DSL规范。
        :return: 删除操作的结果，包括删除的文档数量和是否有未处理的请求。
        """
        try:
            delete_response = self.client.delete_by_query(
                index=index,
                body=query,
                refresh=True  # 立即刷新索引，使删除操作立即生效
            )
            deleted_docs_count = delete_response["deleted"]
            return deleted_docs_count
        except Exception as e:
            print(f"Failed to delete documents by query in index {index}: {e}")
            return 0

    def common_search(self, index, query=None, limit=10, offset=0, order=None):
        """
        执行一个通用的搜索操作。

        :param index: 指定要搜索的索引。
        :param query: 搜索查询语句，可以是任何Elasticsearch支持的查询类型。如果未提供，则默认匹配所有文档。
            {
                "bool": {
                    "must": [
                        {
                            "wildcard": {
                                "key": "*6c2d54a1fb142166cc2c3cf6a"
                            }
                        }
                    ]
                }
            }
        :param limit: 返回结果的最大数量。
        :param offset: 搜索结果的偏移量，用于分页。
        :param order: 指定搜索结果的排序方式，应为一个包含字段和排序顺序的字典或列表。
            {
                "startTime": {
                    "order": "asc"
                },
                "key": {
                    "order": "desc"
                }
            }
        :return: 返回一个包含搜索结果的列表，每个结果都是一个字典形式的文档。
        """
        # 初始化搜索对象并指定使用的索引
        s = Search(using=self.client, index=index)

        # 如果提供了查询语句，则使用提供的查询语句，否则使用匹配所有文档的查询
        if query:
            s = s.query(query)
        else:
            s = s.query({"match_all": {}})

        # 如果提供了排序条件，则对搜索结果进行排序
        if order:
            s = s.sort(order)

        # 执行搜索操作，并从搜索结果中获取指定范围的数据
        data = s[offset:limit].execute()

        # 将搜索结果转换为字典形式的列表
        result = [item.to_dict() for item in data]

        return result


if __name__ == '__main__':
    from elasticsearch_dsl import connections, Search

    ES = {
        'default': {
            'hosts': "http://127.0.0.1:9200",
            # 'http_auth': (ES_USERNAME, ES_PASSWORD)
        }
    }
    connections.configure(**ES)
    client = get_connection()
    e = ElasticSearchManager(client)
    _index = "webssh-login-2024-02"
    query = {
        "bool": {
            "must": [
                {
                    "wildcard": {
                        "key": "*6c2d54a1fb142166cc2c3cf6a"
                    }
                }
            ]
        }

    }
    order = {"startTime": {"order": "asc"}, "key": {"order": "desc"}}
    print(e.common_search(index=_index, query=query, order=order))

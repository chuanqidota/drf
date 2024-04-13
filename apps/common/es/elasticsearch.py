import json
import traceback

from elasticsearch_dsl.connections import get_connection


class ElasticSearchManager(object):
    """
    ES类封装
    """

    def __init__(self):
        # 直接从es连接池中获取连接
        self.client = get_connection()

    def get_index_info(self, index):
        """
        获取索引信息

        :param index: 指定的索引名称。
        :return: 索引信息，如果索引不存在则返回None。
                 {
                     "my_index": {
                         "aliases": {},
                         "mappings": {
                             "properties": {
                                 "field1": {...},
                                 "field2": {...},
                                 ...
                             }
                         },
                         "settings": {
                             "index": {
                                 "number_of_shards": "5",
                                 "number_of_replicas": "1",
                                 ...
                             }
                         }
                     }
                 }
        """
        try:
            # 获取索引信息
            response = self.client.indices.get(index=index)
            # 返回索引信息
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
        return self.client.indices.exists(index=index)

    def create_index(self, index):
        """
        尝试创建一个指定名称的索引，如果该索引不存在的话。

        :param index: 指定的索引名称。
        :return: 布尔值，索引成功创建返回True，否则返回False。
        """
        # 检查索引是否已经存在，如果不存在则尝试创建
        if not self.client.indices.exists(index=index):
            try:
                # 忽略400错误（已存在）进行索引创建，确保索引只在不存在时创建
                response = self.client.indices.create(index=index, ignore=400)
                # 判断索引创建是否成功
                if response["acknowledged"] and response["result"] == "created":
                    return True
                else:
                    return False
            except Exception as e:
                # 创建索引过程中发生异常，返回False
                return False
        else:
            # 索引已存在，无需创建
            return False

    def delete_index(self, index):
        """
        删除指定的索引。

        :param index: 索引的名称，必须是一个非空字符串。
        :return: 如果索引成功被删除则返回True，如果索引不存在或删除操作出现异常则返回False。
        """
        # 校验index参数是否为空或非字符串类型
        if not index or not isinstance(index, str):
            raise ValueError("Index name must be a non-empty string.")
        try:
            # 检查索引是否存在
            if self.client.indices.exists(index=index):
                # 如果存在，则删除该索引
                self.client.indices.delete(index=index)
                return True
            else:
                # 索引不存在，直接返回False
                return False
        except Exception as e:
            # 删除操作出现异常，返回False
            return False

    def update_index(self, index, body):
        """
        更新索引信息

        :param index: 指定的索引名称。
        :param body: 更新的索引信息，应为一个字典结构。
            update_body = {
                "settings": {
                    "number_of_shards": 5,  # 修改索引的分片数为5
                    "number_of_replicas": 1,  # 修改索引的副本数为1
                    "refresh_interval": "30s",  # 设置索引刷新间隔为30秒
                    "analysis": {
                        "analyzer": {
                            "custom_analyzer": {  # 定义一个新的自定义分析器
                                "tokenizer": "standard",
                                "filter": ["lowercase", "asciifolding"]
                            }
                        }
                    }
                }
            }
        :return: 布尔值，索引更新成功返回True，否则返回False。
        """
        try:
            # 更新索引信息
            response = self.client.indices.put_settings(index=index, body=body)
            # 判断索引更新是否成功
            if response["acknowledged"]:
                return True
            else:
                return False
        except Exception as e:
            # 更新索引信息过程中发生异常，返回False
            return False

    def create_index_with_mapping(self, index, mapping):
        """
        创建一个索引并指定其mapping。

        :param index: 索引名称。
        :param mapping: 索引mapping定义，应为一个字典结构。
            {
                 "field1": {...},
                 "field2": {...},
                 ...
            }
        :return: 创建操作是否成功，返回True或False。
        """
        try:
            self.client.indices.create(index=index, body={"mappings": {"properties": mapping}})
            return True
        except Exception as e:
            print(f"Failed to create index {index} with mapping: {e}")
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
            # 获取索引映射信息
            response = self.client.indices.get_mapping(index=index)
            # 返回映射信息
            return response
        except Exception as e:
            # 获取映射信息过程中发生异常，返回None
            return None

    def update_mapping(self, index, mappings):
        """
        向指定索引中设置映射（mapping）。

        :param index: 目标索引名称。
        :param mappings: 映射定义，应为一个字典结构
            {
                 "field1": {...},
                 "field2": {...},
                 ...
            }
        :return: 如果映射设置成功，返回 True；否则返回 False。
        """
        try:
            response = self.client.indices.put_mapping(index=index, body={"properties": mappings})

            # 检查响应状态码，不同 Elasticsearch 客户端库可能会有不同的表示方式，
            # 请根据您实际使用的库查阅文档以获取正确的检查方法。
            # 以下假设 response 对象有一个 'acknowledged' 字段用于指示操作是否被服务器确认。
            if response.get('acknowledged', False):
                return True

            # 如果响应中没有明确的成功标识，也可以尝试检查 HTTP 状态码
            # 若您的客户端库返回的是 requests.Response 类型对象，可以使用如下方式：
            # if response.status_code == 200:
            #     return True

        except Exception as e:
            # 出现异常，打印错误信息并返回 False
            print(f"Failed to put mappings for index {index}: {e}")
            return False

        return False

    def add_field_to_mapping(self, index, field_name, field_mapping):
        """
        向指定索引的mapping中添加新的字段。

        :param index: 索引名称。
        :param field_name: 新增字段的名称。
        :param field_mapping: 新增字段的mapping定义，应为一个字典结构。
        :return: 添加操作是否成功，返回True或False。
        """
        current_mapping = self.get_mapping(index)
        current_properties = current_mapping["properties"]

        updated_properties = {**current_properties, field_name: field_mapping}
        updated_mapping = {"properties": updated_properties}

        return self.update_mapping(index, updated_mapping)

    def insert_document(self, index, document_id, document_data):
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
            self.client.index(index=index, id=document_id, body=document_data)
            return True
        except Exception as e:
            print(f"Failed to insert document into index {index}: {e}")
            return False

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

    def bulk_operation(self, actions):
        """
        执行批量文档操作（插入、更新、删除）。

        :param actions: 一个包含多个操作的列表，每个操作是一个包含两个元素的元组：操作类型（字符串）和操作数据（字典）。
                        [
                          ("index", {"_index": "my_index", "_id": "doc1", "data": {...}}),
                          ("update", {"_index": "my_index", "_id": "doc2", "doc": {...}}),
                          ("delete", {"_index": "my_index", "_id": "doc3"})
                        ]
        :return: 批量操作结果，包含成功、失败、错误等信息的字典。
        """
        try:
            response = self.client.bulk(body=actions)
            return response
        except Exception as e:
            print(f"Failed to perform bulk operation: {e}")
            return {"errors": True, "items": []}

    def basic_search(self, index, query_text, size=10):
        """
        在指定索引中执行基本的全文搜索。

        :param index: 索引名称。
        :param query_text: 搜索文本。
        :param size: 返回结果的最大数量，默认为10。
        :return: 搜索结果，包括命中文档列表和总命中数。
             (
                  [
                      {"field1": "value1", "field2": "value2", ...},
                      {"field1": "value3", "field2": "value4", ...},
                      ...
                  ],
                  25
            )
        """
        search_body = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["*"],  # 搜索所有字段
                    "type": "most_fields"  # 使用最匹配字段组合得分
                }
            },
            "size": size
        }

        response = self.client.search(index=index, body=search_body)

        hits = [hit["_source"] for hit in response["hits"]["hits"]]
        total_hits = response["hits"]["total"]["value"]

        return hits, total_hits

    def exact_match_search(self, index, field, value, size=10):
        """
        在指定索引中执行精确匹配搜索。

        :param index: 索引名称。
        :param field: 字段名。
        :param value: 待匹配的值。
        :param size: 返回结果的最大数量，默认为10。
        :return: 精确匹配的文档列表和总命中数。
             (
                  [
                      {"field1": "match_value", "field2": "value2", ...},
                      {"field1": "match_value", "field2": "value4", ...},
                      ...
                  ],
                  25
            )
        """
        search_body = {
            "query": {
                "term": {
                    field: value
                }
            },
            "size": size
        }

        response = self.client.search(index=index, body=search_body)

        hits = [hit["_source"] for hit in response["hits"]["hits"]]
        total_hits = response["hits"]["total"]["value"]

        return hits, total_hits

    def boolean_search(self, index, must_clauses=[], should_clauses=[], must_not_clauses=[], size=10):
        """
        在指定索引中执行布尔查询。

        :param index: 索引名称。
        :param must_clauses: 必须满足的查询条件列表。
        :param should_clauses: 可选满足的查询条件列表，至少满足一个。
        :param must_not_clauses: 必须不满足的查询条件列表。
        :param size: 返回结果的最大数量，默认为10。
        :return: 符合布尔查询条件的文档列表和总命中数。
        """
        bool_query = {
            "must": must_clauses,
            "should": should_clauses,
            "must_not": must_not_clauses
        }

        search_body = {
            "query": {
                "bool": bool_query
            },
            "size": size
        }

        response = self.client.search(index=index, body=search_body)

        hits = [hit["_source"] for hit in response["hits"]["hits"]]
        total_hits = response["hits"]["total"]["value"]

        return hits, total_hits

    def aggregation_search(self, index, aggregations, query=None, size=0):
        """
        在指定索引中执行聚合查询。

        :param index: 索引名称。
        :param aggregations: 聚合定义，字典形式。
        :param query: 可选，基础查询条件（影响聚合结果的文档集）。
        :param size: 通常设为0，表示仅返回聚合结果，不返回命中的文档。
        :return: 聚合结果字典。
        """
        search_body = {
            "size": size,
            "aggs": aggregations
        }
        if query is not None:
            search_body["query"] = query

        response = self.client.search(index=index, body=search_body)

        return response["aggregations"]

    def search(self, index=None, body=None, **params):
        """
        查询方法，如梦查询异常，根据ES的return格式，返回空数据
        :param index:
        :param body:
        :param params:
        :return:
        """
        try:
            # 如果不存在该Index忽略报错, 将不会抛出异常
            if 'ignore_unavailable' not in params:
                params['ignore_unavailable'] = True
            ret = self.client.search(index, json.dumps(body), **params)
        except Exception as e:
            print(repr(e))
            print(traceback.format_exc())
            return {'hits': {'hits': [], 'total': 0}}
        return ret

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
            has_failures = delete_response["hasFailures"]

            return deleted_docs_count, has_failures
        except Exception as e:
            print(f"Failed to delete documents by query in index {index}: {e}")
            return 0, True

    def common_search(self, index=None, body=None, ignore_unavailable=True, **params):
        """
        查询方法。如遇查询异常，根据Elasticsearch返回格式，返回空数据。

        :param index: 索引名称。
        :param body: 查询体，应为一个字典。
        :param ignore_unavailable: 是否忽略不存在的索引。默认为True。
        :param params: 其他查询参数。
        :return: 查询结果，若出现异常则返回模拟的空数据。
        """
        params['ignore_unavailable'] = ignore_unavailable

        if body and not isinstance(body, dict):
            raise ValueError("The 'body' parameter must be a dictionary.")
        try:
            response = self.client.search(index, json.dumps(body) if body else None, **params)
        except Exception as e:
            # 特殊处理索引未找到的异常，返回空数据
            return {'hits': {'hits': [], 'total': 0}}
        return response

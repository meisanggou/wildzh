# !/usr/bin/env python
# coding: utf-8
import json
import elasticsearch
from elasticsearch.exceptions import NotFoundError
import uuid

__author__ = 'zhouhenglc'


class ExamEs(object):

    def __init__(self):
        host = '192.168.152.133'
        port = '9200'
        ent = {"host": host, "port": port}
        self.es_man = None # elasticsearch.Elasticsearch(hosts=[ent])
        self.index = 'exam_v1'
        self.index_type = 'exam'
        self.index_fields = ['desc', 'options', 'answer']
        self.create_index()

    def create_index(self):
        if not self.es_man:
            return
        if self.es_man.indices.exists(self.index):
            return
        properties = {}
        index_p = {'index': True,
                   'type': 'text',
                   'analyzer': 'ik_max_word',
                   'search_analyzer': 'ik_max_word'}
        for field in self.index_fields:
            properties[field] = index_p
        body = {'mappings': {'properties': properties}}
        self.es_man.indices.create(self.index, body=body)

    def add_one(self, doc_id, body):
        res = self.es_man.index(index=self.index, id=doc_id, body=body)
        return res

    def update_one(self, doc_id, body):
        doc = {'doc': body}
        res = self.es_man.update(self.index, doc_id, doc)
        return res

    def update_one_item(self, doc_id, desc, options, answer):
        body = {'desc': desc, 'options': options, 'answer': answer}
        try:
            res = self.update_one(doc_id, body)
        except NotFoundError:
            res = self.add_one(doc_id, body)
        return res

    def add_one_item(self, doc_id, desc, options, answer):
        body = {'desc': desc, 'options': options, 'answer': answer}
        return self.add_one(doc_id, body)

    def exists(self, doc_id):
        r = self.es_man.exists(self.index, doc_id)
        return r

    def get_one(self, doc_id):
        r = self.es_man.get(self.index, doc_id)
        return r

    def clear_index(self):
        body = {"query": {"match_all": {}}}
        r = self.es_man.delete_by_query(self.index, body=body)

    def search(self, s, field=None):
        if field not in self.index_fields:
            field = self.index_fields[0]
        res = self.es_man.search(index=self.index,
                                 body={"query": {"match": {field: s}}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        for hit in res['hits']['hits']:
            print(hit)
            print("%(desc)s %(options)s: %(answer)s" % hit["_source"])

    def search_multi(self, s, fields=None):
        if fields is None:
            fields = self.index_fields
        else:
            fields = list(set(self.index_fields) & set(fields))
        if len(fields) <= 0:
            return []
        res = self.es_man.search(index=self.index,
                                 body={
                                     "query": {
                                         "multi_match": {
                                             'query': s,
                                             'fields': fields}}})
        q_items = []
        for hit in res['hits']['hits']:
            print(hit)
            q_item = {'_id': hit['_id'], '_score': hit['_score']}
            q_item.update(hit["_source"])
        return q_items


if __name__ == "__main__":
    ee = ExamEs()
    doc_id = uuid.uuid4().hex
    ee.clear_index()
    # ee.add_one_item(doc_id, '网络操作', '编辑网络', '创建网络，vlan网络类型不可编辑，如果多个网络类型，默认选择第一个')
    # ee.search_multi('网络类型 vlan')
    # ee.update_one_item('1111111', '网络操作2', '更新网络', '网络都是vlan的')
    # ee.get_one(doc_id)
    # ee.get_one('1111111111')

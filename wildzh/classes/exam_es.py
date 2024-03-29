# !/usr/bin/env python
# coding: utf-8
import json
import elasticsearch
from elasticsearch.exceptions import NotFoundError
import uuid

from wildzh.utils.config import ConfigLoader

__author__ = 'zhouhenglc'


class ExamEs(object):

    def __init__(self, es_conf):
        cl = ConfigLoader(es_conf)
        host = cl.get('es', 'host')
        port = cl.get('es', 'port')
        ent = {"host": host, "port": port}
        self._es_man = None
        self.es_endpoint = ent
        self.index = 'exam_v3'
        self.index_type = 'exam'
        self.index_fields = ['desc', 'options', 'answer']
        self.no_index_fields = ['exam_no']

    @property
    def es_man(self):
        if self._es_man is None:
            hosts = [self.es_endpoint]
            self._es_man = elasticsearch.Elasticsearch(hosts=hosts)
            self.create_index()
        return self._es_man

    def delete_index(self):
        return self.es_man.indices.delete(self.index)

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
        no_index_p = {'type': 'text'}
        for field in self.no_index_fields:
            properties[field] = no_index_p
        body = {'mappings': {'properties': properties}}
        self.es_man.indices.create(self.index, body=body)

    def re_create_index(self):
        self.delete_index()
        self.create_index()

    def add_one(self, doc_id, body):
        res = self.es_man.index(index=self.index, id=doc_id, body=body)
        return res

    def update_one(self, doc_id, body):
        doc = {'doc': body}
        res = self.es_man.update(self.index, doc_id, doc)
        return res

    def update_one_item(self, doc_id, exam_no, desc, options, answer,
                        select_mode=None):
        body = {'desc': desc, 'options': options, 'answer': answer,
                'sm': select_mode}
        try:
            res = self.update_one(doc_id, body)
        except NotFoundError:
            body['exam_no'] = exam_no
            res = self.add_one(doc_id, body)
        return res

    def add_one_item(self, doc_id, exam_no, desc, options, answer,
                     select_mode=None):
        body = {'exam_no': exam_no, 'desc': desc, 'options': options,
                'answer': answer, 'sm': select_mode}
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
        return r

    def clear_exam(self, exam_no):
        query = {"constant_score" :
                     {"filter" :
                          {"term" : { "exam_no" : exam_no} } } }
        body = {'query': query}
        r = self.es_man.delete_by_query(self.index, body=body)
        return r

    def search(self, s, field=None):
        if field not in self.index_fields:
            field = self.index_fields[0]
        res = self.es_man.search(index=self.index,
                                 body={"query": {"match": {field: s}}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        for hit in res['hits']['hits']:
            print(hit)
            print("%(desc)s %(options)s: %(answer)s" % hit["_source"])

    def count_exam(self, exam_no):
        query = {"constant_score" :
                     {"filter" :
                          {"term" : { "exam_no" : exam_no} } } }
        body = {'query': query}
        res = self.es_man.count(index=self.index, body=body)
        return res['count']


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
            q_item = {'_id': hit['_id'], 'score': hit['_score']}
            q_item.update(hit["_source"])
            q_items.append(q_item)
        return q_items


if __name__ == "__main__":
    ee = ExamEs('../../etc/es.conf')
    # ee.re_create_index()
    # doc_id = uuid.uuid4().hex
    # ee.clear_index()
    # ee.add_one_item(doc_id, '网络操作', '编辑网络', '创建网络，vlan网络类型不可编辑，如果多个网络类型，默认选择第一个')
    print(ee.count_exam('1567228509'))
    print(ee.clear_exam('1567228509'))
    # ee.update_one_item('1111111', '网络操作2', '更新网络', '网络都是vlan的')
    # ee.get_one(doc_id)
    # ee.get_one('1111111111')

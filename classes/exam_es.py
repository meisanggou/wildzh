# !/usr/bin/env python
# coding: utf-8
import json
import elasticsearch
import uuid

__author__ = 'zhouhenglc'


class ExamEs(object):

    def __init__(self):
        host = '192.168.152.133'
        port = '9200'
        ent = {"host": host, "port": port}
        self.es_man = elasticsearch.Elasticsearch(hosts=[ent])
        self.index = 'exam'
        self.create_index()

    def create_index(self):
        self.es_man.create()

    def add_one(self, doc_id, body):
        res = self.es_man.index(index=self.index, id=doc_id, body=body)
        print(res)
        return res

    def add_one_item(self, doc_id, desc, options, answer):
        body = {'desc': desc, 'options': options, 'answer': answer}
        return self.add_one(doc_id, body)

    def search(self, s):
        res = self.es_man.search(index=self.index, body={"query": {"match": {'answer': s}}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        for hit in res['hits']['hits']:
            print(hit)
            print("%(desc)s %(options)s: %(answer)s" % hit["_source"])

if __name__ == "__main__":
    ee = ExamEs()
    doc_id = uuid.uuid4().hex
    # ee.add_one_item(doc_id, '网络操作', '编辑网络', '创建网络，网络类型不可编辑，如果多个网络类型，默认选择第一个')
    ee.search('网络类型 vxlan')

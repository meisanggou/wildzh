# !/usr/bin/env python
# coding: utf-8
from wildzh.classes import DBObject

__author__ = 'zhouhenglc'


class ExamAD(DBObject):
    table = 'exam_ad'
    columns = ['exam_no', 'ad_desc', 'ignore_interval', 'enabled']

    def insert_or_update(self, exam_no, ad_desc, ignore_interval=36, enabled=False):
        data = dict(exam_no=exam_no, ad_desc=ad_desc,
                    ignore_interval=ignore_interval, enabled=enabled)
        u_keys = ['ad_desc', 'ignore_interval', 'enabled']
        l = self.db.execute_duplicate_insert(self.t, kwargs=data,
                                             u_keys=u_keys)
        return l

    def select(self, exam_no):
        where_value = dict(exam_no=exam_no)
        items = self.db.execute_select(self.t, where_value=where_value,
                                       cols=self.cols)
        if len(items) > 0:
            return items[0]
        default = {'exam_no': exam_no, 'ad_desc': '', 'ignore_interval': 36,
                   'enabled': False}
        return default

    def update_ad(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.cols:
                del kwargs[key]
        self.insert_or_update(**kwargs)

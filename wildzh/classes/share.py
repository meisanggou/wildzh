# !/usr/bin/env python
# coding: utf-8
import random
from wildzh.classes import DBObject

__author__ = 'zhouhenglc'


class ShareKey(DBObject):
    table = 'share_key'
    columns = ['user_no', 'share_key', 'last_modify']

    @staticmethod
    def gen_key(user_no):
        rn = random.randint(0, 4095)
        rn_s = hex(rn)[2:].zfill(3)
        u_s = hex(user_no)[2:].zfill(5)[::-1]
        return '%s%s' % (u_s, rn_s)

    def create(self, user_no, may_exist=True):
        if may_exist:
            exist_item = self.select(user_no)
            if exist_item:
                return exist_item
        share_key = self.gen_key(user_no)
        data = dict(user_no=user_no, share_key=share_key,
                    last_modify=self.now_time)
        l = self.db.execute_insert(self.t, kwargs=data)
        return l

    def select(self, user_no):
        where_value = dict(user_no=user_no)
        items = self.db.execute_select(self.t, where_value=where_value,
                                       cols=self.cols)
        if len(items) > 0:
            return items[0]
        return None


class ShareRecords(DBObject):
    table = 'share_records'
    columns = ['user_no', 'resource', 'resource_id', 'inviter', 'share_token',
               'extend', 'insert_time']

    def create(self, user_no, resource, resource_id, inviter, share_token, extend):
        data = dict(user_no=user_no, resource=resource,
                    resource_id=resource_id, inviter=inviter,
                    share_token=share_token, extend=extend,
                    insert_time=self.now_time)
        l = self.db.execute_insert(self.t, kwargs=data)
        return l

    def select(self, user_no, share_token=None):
        where_value = dict(user_no=user_no)
        if share_token is not None:
            where_value['share_token'] = share_token
        items = self.db.execute_select(self.t, where_value=where_value,
                                       cols=self.cols)
        if len(items) > 0:
            return items[0]
        return None

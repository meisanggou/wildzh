# !/usr/bin/env python
# coding: utf-8

import re
import time
import json
import random
import string
from mysqldb_rich.db2 import DB

__author__ = 'meisa'

"""
班级角色值解释
0创建者 1管理员 2-9保留
10成员 11-19保留
20申请者 21申请者（曾被拒绝） 22申请者（曾被踢出） 23申请者（曾自己退出） 23-29保留
30拒绝加入 31被踢出 32自己退出
"""


class MyClass(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t_info = "class_info"
        self.t_m = "class_member"
        self.t_r = "class_resource"

    def insert_info(self, user_no, class_name, class_desc, quota=100):
        # 查询班级数 一个账户最多5个班级
        c_items = self.select_my_class(user_no)
        pass

    def insert_member(self):
        pass

    def insert_resource(self):
        pass

    def select_info(self, class_no):
        pass

    def _select_class_member(self, class_no=None, user_no=None, min_role=0, max_role=100):
        cols = ["class_no", "user_no", "role", "user_remark", "add_time", "update_time"]
        where_value = dict()
        if user_no is not None:
            where_value["user_no"] = user_no
        if class_no is not None:
            where_value["class_no"] = class_no
        items = self.db.execute_select(self.t_info, where_value=where_value, cols=cols)
        real_items = filter(lambda x: min_role <= x["role"] <= max_role, items)
        return real_items

    def select_my_class(self, user_no, max_role=19):
        real_items = self._select_class_member(user_no=user_no, max_role=max_role)
        return real_items

    def select_member(self, class_no):
        pass

    def select_resource(self, class_no, resource_type):
        pass

    def remove_info(self, class_no):
        pass

    def remove_member(self, class_no, user_no):
        pass

    def remove_resource(self, class_no, resource_type, resource_id):
        pass

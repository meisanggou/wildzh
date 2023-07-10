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
30拒绝加入 31被踢出 32自己退出 33放弃申请
99无任何关联（不存在于数据库中）
"""


class MyClassInfo(object):

    def __init__(self, db):
        self.db = db
        self.t = "class_info"

    def insert_info(self, user_no, class_name, class_desc, quota=100):
        add_time = time.time()
        kwargs = dict(user_no=user_no, class_name=class_name, class_desc=class_desc, quota=quota, add_time=add_time)
        self.db.start_transaction()
        try:
            l = self.db.execute_insert(self.t, kwargs=kwargs)
            cols = ["class_no", "class_name", "class_desc", "user_no", "num", "quota", "add_time"]
            items = self.db.execute_select(self.t, cols=cols, limit=1, order_desc=True, order_by=["class_no"])
        except Exception:
            self.db.end_transaction(fail=True)
            return None
        self.db.end_transaction()
        if len(items) <= 0:
            return None
        return items[0]

    def select_info(self, class_no):
        cols = ["class_no", "class_name", "class_desc", "user_no", "num", "quota", "add_time"]
        if isinstance(class_no, int) is True:
            where_value = dict(class_no=class_no)
            items = self.db.execute_select(self.t, cols=cols, where_value=where_value)
        elif isinstance(class_no, list) is True:
            where_value = dict(class_no=class_no)
            items = self.db.execute_multi_select(self.t, where_value=where_value, cols=cols)
        else:
            return []
        return items

    def remove_info(self, class_no):
        where_value = dict(class_no=class_no)
        l = self.db.execute_delete(self.t, where_value=where_value)
        return l


class MyClassMember(object):

    def __init__(self, db):
        self.db = db
        self.t = "class_member"

    def insert_member(self, class_no, user_no, role, user_remark):
        add_time = time.time()
        update_time = add_time
        kwargs = dict(class_no=class_no, user_no=user_no, role=role, user_remark=user_remark, add_time=add_time,
                      update_time=update_time)
        l = self.db.execute_insert(self.t, kwargs=kwargs)
        return l

    def _select_class_member(self, class_no=None, user_no=None, min_role=0, max_role=100):
        cols = ["class_no", "user_no", "role", "user_remark", "add_time", "update_time"]
        where_value = dict()
        if user_no is not None:
            where_value["user_no"] = user_no
        if class_no is not None:
            where_value["class_no"] = class_no
        items = self.db.execute_select(self.t, where_value=where_value, cols=cols)
        real_items = filter(lambda x: min_role <= x["role"] <= max_role, items)
        return real_items

    def select_my_class(self, user_no, max_role=19):
        real_items = self._select_class_member(user_no=user_no, max_role=max_role)
        return real_items

    def select_member(self, class_no):
        items = self._select_class_member(class_no, max_role=29)
        return items

    def select_role(self, class_no, user_no):
        items = self._select_class_member(class_no, user_no)
        if len(items) < 0:
            return 99
        else:
            return items[0]["role"]

    def update_member(self, class_no, user_no, role):
        update_value = dict(role=role)
        where_value = dict(class_no=class_no, user_no=user_no)
        l = self.db.execute_update(self.t, update_value=update_value, where_value=where_value)
        return l


class MyClassResource(object):

    def __init__(self, db):
        self.db = db
        self.t = "class_resource"

    def insert_resource(self, class_no, resource_type, resource_id, user_no):
        add_time = time.time()
        kwargs = dict(class_no=class_no, resource_type=resource_type, resource_id=resource_id, user_no=user_no,
                      add_time=add_time)
        l = self.db.execute_insert(self.t, kwargs=kwargs, ignore=True)
        if l <= 0:
            return None
        return kwargs

    def select_resource(self, class_no, resource_type):
        cols = ["class_no", "resource_type", "resource_id", "user_no", "add_time"]
        where_value = dict(class_no=class_no, resource_type=resource_type)
        items = self.db.execute_select(self.t, where_value=where_value, cols=cols)
        return items

    def delete_resource(self, class_no, resource_type, resource_id):
        where_value = dict(class_no=class_no, resource_type=resource_type, resource_id=resource_id)
        l = self.db.execute_delete(self.t, where_value=where_value)
        return l


class MyClass(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.man_info = MyClassInfo(self.db)
        self.man_mem = MyClassMember(self.db)
        self.man_res = MyClassResource(self.db)

    def new_class(self, user_no, class_name, class_desc, quota):
        # 每个人最多管理5个班级
        items = self.man_mem.select_my_class(user_no, max_role=9)
        if len(items) >= 5:
            return False, "管理班级数已达到上线"
        if quota > 100:
            quota = 100
        c_item = self.man_info.insert_info(user_no, class_name[:20], class_desc[:200], quota)
        if c_item is None:
            return False, "请重试"
        l = self.man_mem.insert_member(c_item["class_no"], user_no, 0, "创建者")
        if l <= 0:
            return False, "创建失败"
        return True, c_item

    def new_resource(self, class_no, resource_type, resource_id, user_no):
        # 检查用户是否有权限 添加资源
        role = self.man_mem.select_role(class_no, user_no)
        if role > 9:
            return False, "无权限操作"
        r_item = self.man_res.insert_resource(class_no, resource_type, resource_id, user_no)
        if r_item is None:
            return False, "已存在"
        return True, r_item


if __name__ == "__main__":
    c_man = MyClass(db_conf_path="../mysql_app.conf")
    print(c_man.new_class(3, "软考", "软考学习班", 50))

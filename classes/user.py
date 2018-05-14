# !/usr/bin/env python
# coding: utf-8

import time
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from mysqldb_rich import DB

__author__ = 'meisa'


class User(object):

    _salt_password = "msg_zh2018"

    @staticmethod
    def _md5_hash(s):
        m = hashlib.md5()
        if isinstance(s, unicode) is True:
            s = s.encode("utf-8")
        m.update(s)
        return m.hexdigest()

    @staticmethod
    def _md5_hash_password(user_name, password):
        md5_password = User._md5_hash(user_name + password + user_name)
        return (md5_password + User._salt_password).upper()

    @staticmethod
    def _password_check(password, db_password, user_name):
        if db_password is None:
            return False  # 密码为空 无限期禁止登录
        if len(password) <= 20:
            if check_password_hash(db_password, User._md5_hash_password(user_name, password)) is True:
                return True
        return False

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t = "sys_user"

    # 插入用户注册数据
    def insert_user(self, user_name, password=None, tel=None, nick_name=None, email=None, wx_id=None, creator=None,
                    role=1):
        add_time = int(time.time())
        kwargs = dict(user_name=user_name, password=password, tel=tel, nick_name=nick_name, email=email, wx_id=wx_id,
                      creator=creator, add_time=add_time, role=role)
        if password is not None:
            kwargs["password"] = generate_password_hash(self._md5_hash_password(user_name, password))
        l = self.db.execute_insert(self.t, kwargs=kwargs, ignore=True)
        return l

    def update_password(self, user_name, new_password):
        en_password = generate_password_hash(self._md5_hash_password(user_name, new_password))
        update_value = {"password": en_password}
        result = self.db.execute_update(self.t, update_value=update_value, where_value={"user_name": user_name})
        return result

    # 验证auth是否存在 包括 account tel alias wx_id
    def verify_user_exist(self, **kwargs):
        cols = ["user_name", "tel", "email", "wx_id", "role"]
        if kwargs.pop("need_password", None) is not None:
            cols.append("password")
        db_items = self.db.execute_select(self.t, where_value=kwargs, cols=cols, package=True)
        return db_items

    def new_user(self, user_name, password=None, nick_name=None, creator=None, role=1):
        items = self.verify_user_exist(user_name=user_name)
        if len(items) > 0:
            return False, u"用户名已存在"

        if nick_name is None:
            nick_name = user_name
        self.insert_user(user_name, password, nick_name=nick_name, creator=creator, role=role)
        return True, dict(user_name=user_name)

    def user_confirm(self, password, user_name=None, email=None, tel=None):
        if user_name is not None:
            where_value = dict(user_name=user_name)
        elif email is not None:
            where_value = {"email": email}
        elif tel is not None:
            where_value = {"tel": tel}
        else:
            return -3, None
        where_value["need_password"] = True
        db_items = self.verify_user_exist(**where_value)
        if len(db_items) <= 0:
            return -2, None
        user_item = db_items[0]
        account = user_item["user_name"]
        db_password = user_item["password"]
        if self._password_check(password, db_password, account) is False:
            return -1, None
        del user_item["password"]
        return 0, user_item


if __name__ == "__main__":
    import os
    import sys
    script_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(script_dir)
    from zh_config import db_conf_path
    um = User(db_conf_path)
    if len(sys.argv) >= 3:
        u = sys.argv[1]
        p = sys.argv[2]
    else:
        u = p = "admin"
    r, item = um.new_user(u, password=p)
    if r is False:
        print("update password")
        um.update_password(u, p)
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
    def _md5_hash_password(account, password):
        md5_password = User._md5_hash(account + password + account)
        return (md5_password + User._salt_password).upper()

    @staticmethod
    def _password_check(password, db_password, account):
        if db_password is None:
            return False  # 密码为空 无限期禁止登录
        if len(password) <= 20:
            if check_password_hash(db_password, User._md5_hash_password(account, password)) is True:
                return True
        return False

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t = "sys_user"

    # 插入用户注册数据
    def insert_user(self, account, password=None, tel=None, alias=None, union_id=None, wx_id=None):
        kwargs = dict(account=account, password=password, tel=tel, alias=alias, union_id=union_id, wx_id=wx_id)
        if password is not None:
            kwargs["password"] = generate_password_hash(self._md5_hash_password(account, password))
        l = self.db.execute_insert(self.t, kwargs=kwargs, ignore=True)
        return l

    def update_password(self, account, new_password):
        en_password = generate_password_hash(self._md5_hash_password(account, new_password))
        update_value = {"password": en_password, "login_success": 1, "unlock_time": None}
        result = self.db.execute_update(self.t, update_value=update_value, where_value={"account": account})
        return result

    # 验证auth是否存在 包括 account tel alias wx_id
    def verify_user_exist(self, **kwargs):
        cols = ["user_name", "tel", "email", "wx_id", "role"]
        if kwargs.pop("need_password", None) is not None:
            cols.append("password")
        db_items = self.db.execute_select(self.t, where_value=kwargs, cols=cols, package=True)
        return db_items

    def new(self, user_name, nick_name, creator, role=1):
        items = self.verify_user_exist(user_name=user_name)
        if len(items) > 0:
            return False, u"用户名已存在"
        add_time = int(time.time())
        kwargs = dict(user_name=user_name, nick_name=nick_name, creator=creator, role=role, add_time=add_time)
        self.db.execute_insert(self.t, kwargs=kwargs)
        return True, kwargs

    def user_confirm(self, password, email=None, tel=None):
        if email is not None:
            where_value = {"email": email}
        elif tel is not None:
            where_value = {"tel": tel}
        else:
            return -3, None
        where_value["need_password"] = True
        db_items = self.verify_user_exist(**where_value)
        if len(db_items) <= 0:
            if email is None:
                return -2, None
        user_item = db_items[0]
        account = user_item["account"]
        db_password = user_item["password"]
        if self._password_check(password, db_password, account) is False:
            return -1, None
        del user_item["password"]
        return 0, user_item



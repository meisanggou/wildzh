# !/usr/bin/env python
# coding: utf-8
import time
from mysqldb_rich.db2 import DB
__author__ = 'meisa'

# 2018-05-28 00:30:00 in UTC
EPOCH = 1527467400


class Comment(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t = "comment_info"

    @staticmethod
    def to_hex(number, z_width=8):
        hex_number = "%x" % number
        hex_number = hex_number.zfill(z_width).upper()
        return hex_number

    @staticmethod
    def to_decimal(hex_number):
        print(hex_number)
        number = int(hex_number, 16)
        return number

    @staticmethod
    def get_timestamp():
        return int(time.time() - EPOCH)

    @property
    def add_time(self):
        return int(time.time())

    @staticmethod
    def create_comment(user_no):
        """

        :param user_no: int11
        :return billing_no: timestamp(8) + user_no(8) + 0(4)
        """
        hex_time = Comment.to_hex(Comment.get_timestamp())
        hex_user_no = Comment.to_hex(user_no)
        hex_project_no = Comment.to_hex(0, z_width=4)
        comment_id = "%s%s%s" % (hex_time, hex_user_no, hex_project_no)
        return comment_id

    def _insert_comment(self, resource_id, comment_id, content, owner, anonymous=0):
        kwargs = dict(resource_id=resource_id, comment_id=comment_id, content=content, owner=owner,
                      add_time=self.add_time, anonymous=anonymous)
        l = self.db.execute_insert(self.t, kwargs=kwargs, ignore=True)
        if anonymous:
            kwargs["owner"] = None
        return l, kwargs

    def _select_comment(self, resource_id, comment_id=None):
        cols = ["resource_id", "comment_id", "content", "owner", "add_time", "anonymous"]
        where_value = dict(resource_id=resource_id)
        if comment_id is not None:
            prefix_value = comment_id[:-4]
        else:
            prefix_value = None
        items = self.db.execute_select_with_lock(self.t, where_value=where_value, prefix_value=prefix_value, cols=cols)
        for item in items:
            if item["anonymous"] is True:
                item["owner"] = None
        return items

    def _new_comment(self, resource_id, content, user_no, anonymous):
        comment_id = self.create_comment(user_no)
        l, data = self._insert_comment(resource_id, comment_id, content, user_no, anonymous)
        if l <= 0:
            return False, "Try Again"
        return True, data

    def _new_comment2(self, resource_id, comment_id, content, user_no, anonymous):
        try:
            self.db.start_transaction()
            items = self._select_comment(resource_id, comment_id)
            if len(items) <= 0:
                return False, "Origin Comment Not Exist"
            last_comment_id = items[-1]["comment_id"]
            next_id = Comment.to_decimal(last_comment_id[-4:]) + 1
            new_id = last_comment_id[:-4] + Comment.to_hex(next_id, 4)
            l, data = self._insert_comment(resource_id, new_id, content, user_no, anonymous)
            if l <= 0:
                return False, "Try Again"
            self.db.end_transaction()
            return True, data
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print(e)
            self.db.end_transaction(fail=True)
            return False, "Internal Error 99"

    def new_comment(self, resource_id, content, user_no, comment_id=None, anonymous=0):
        if comment_id is None:
            return self._new_comment(resource_id, content, user_no, anonymous)
        else:
            return self._new_comment2(resource_id, comment_id, content, user_no, anonymous)

    def select_comment(self, resource_id):
        items = self._select_comment(resource_id)
        return items

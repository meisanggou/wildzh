# !/usr/bin/env python
# coding: utf-8

import time
import json
from mysqldb_rich import DB

__author__ = 'meisa'


class Music(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t_info = "music_info"
        self.t_records = "listen_records"

    def _insert_info(self, music_type, music_no, music_name, music_desc, music_url, adder, status=1, music_extend=None):
        kwargs = dict(music_type=music_type, music_no=music_no, music_name=music_name, music_desc=music_desc,
                      music_url=music_url, status=status, music_extend=music_extend, adder=adder)
        l = self.db.execute_insert(self.t_info, kwargs=kwargs, ignore=True)
        return l

    def _insert_records(self, user_id, music_no, progress):
        insert_time = int(time.time())
        kwargs = dict(music_no=music_no, progress=progress, insert_time=insert_time, user_id=user_id)
        l = self.db.execute_insert(self.t_records, kwargs=kwargs, ignore=True)
        return l

    def _update_info(self, music_type, music_no, **update_value):
        where_value = dict(music_no=music_no, music_type=music_type)
        l = self.db.execute_update(self.t_info, update_value=update_value, where_value=where_value)
        return l
    
    def _update_status(self, music_no, add_status=None, sub_status=None):
        where_value = dict(music_no=music_no)
        if add_status is not None:
            l = self.db.execute_update(self.t_info, update_value_list=["status=status|%s" % add_status],
                                       where_value=where_value)
        elif sub_status is not None:
            l = self.db.execute_update(self.t_info, update_value_list=["status=status&~%s" % sub_status],
                                       where_value=where_value)
        else:
            l = 0
        return l

    def _update_num(self, music_type, music_no):
        where_value = dict(music_no=music_no, music_type=music_type)
        l = self.db.execute_plus(self.t_info, "listen_num", where_value=where_value)
        return l

    def new_music(self, music_name, music_type, music_desc, music_url, adder, **music_extend):
        music_no = int(time.time())
        l = self._insert_info(music_type, music_no, music_name, music_desc, music_url, adder, music_extend=music_extend)
        if l <= 0:
            return False, l
        return True, music_no
    
    def new_music_record(self, user_id, music_type, music_no, progress):
        self._insert_records(user_id, music_no, progress)
        self._update_num(music_type, music_no)
        return True, None
    
    def select_music(self, music_type, music_no=None):
        where_value = dict()
        where_cond = ["status<>0"]
        if music_type is not None:
            where_value = dict(music_type=music_type)
            if music_no is not None:
                where_value["music_no"] = music_no
        cols = ["music_type", "music_no", "music_name", "music_desc", "music_url", "adder", "status",
                "music_extend", "listen_num"]
        items = self.db.execute_select(self.t_info, cols=cols, where_value=where_value, where_cond=where_cond)
        for item in items:
            if item["music_extend"] is not None:
                item.update(json.loads(item["music_extend"]))
                del item["music_extend"]
        return items
    
    def online_music(self, music_no):
        l = self._update_status(music_no, add_status=64)
        return l

    def delete_music(self, music_type, music_no):
        l = self._update_info(music_type, music_no, status=0)
        return l

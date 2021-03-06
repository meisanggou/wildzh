# !/usr/bin/env python
# coding: utf-8

import time
import json
import uuid
import re
from mysqldb_rich import DB

__author__ = 'meisa'


class Video(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t_info = "video_info"
        self.t_episode = "video_episode"

    def _insert_info(self, video_type, video_no, video_name, video_desc, episode_num, video_pic, accept_formats, adder,
                     status=1, video_extend=None, link_people=None):
        kwargs = dict(video_type=video_type, video_no=video_no, video_name=video_name, video_desc=video_desc,
                      episode_num=episode_num, status=status, video_extend=video_extend, adder=adder,
                      video_pic=video_pic, insert_time=int(time.time()), accept_formats=accept_formats,
                      link_people=link_people)
        l = self.db.execute_insert(self.t_info, kwargs=kwargs, ignore=True)
        return l

    def _insert_episode(self, video_no, episode_index, title, episode_url, episode_pic=None):
        kwargs = dict(video_no=video_no, episode_index=episode_index, title=title, episode_pic=episode_pic,
                      insert_time=int(time.time()), episode_url=episode_url)
        l = self.db.execute_insert(self.t_episode, kwargs=kwargs, ignore=True)
        return l

    def _update_info(self, video_type, video_no, where_cond=None, **update_value):
        where_value = dict(video_no=video_no, video_type=video_type)
        l = self.db.execute_update(self.t_info, update_value=update_value, where_value=where_value,
                                   where_cond=where_cond)
        return l

    def _update_num(self, video_type, video_no):
        where_value = dict(video_type=video_type, video_no=video_no)
        l = self.db.execute_plus(self.t_info, "upload_num", where_value=where_value)
        return l

    def _update_listen_num(self, video_type, video_no, episode_index):
        self.db.execute_plus(self.t_info, "listen_num", where_value=dict(video_no=video_no, video_type=video_type))
        self.db.execute_plus(self.t_episode, "listen_num", where_value=dict(video_no=video_no,
                                                                            episode_index=episode_index))
        return True

    def _update_status(self, video_no, add_status=None, sub_status=None):
        where_value = dict(video_no=video_no)
        if add_status is not None:
            l = self.db.execute_logic_or(self.t_info, status=add_status, where_value=where_value)
        elif sub_status is not None:
            l = self.db.execute_logic_non(self.t_info, where_value=where_value, status=sub_status)
        else:
            l = 0
        return l

    def new_video(self, video_name, video_type, video_desc, episode_num, video_pic, accept_formats, link_people,
                  adder):
        video_no = uuid.uuid4().hex
        l = self._insert_info(video_type, video_no, video_name, video_desc, episode_num, video_pic, accept_formats,
                              adder, link_people=link_people)
        if l <= 0:
            return False, l
        return True, video_no

    def new_video_episode(self, video_type, video_no, episode_index, title, episode_url, episode_pic=None):
        l = self._insert_episode(video_no, episode_index, title, episode_url, episode_pic)
        if l == 1:
            self._update_num(video_type, video_no)
        return l

    def update_video(self, video_type, video_no, **kwargs):
        cols = ["video_name", "video_desc", "episode_num", "video_extend", "video_pic"]
        update_value = dict()
        for key in kwargs.keys():
            if key not in cols:
                continue
            if kwargs[key] is None:
                continue
            update_value[key] = kwargs[key]
        if "upload_num" in kwargs and "episode_num" in kwargs and kwargs["episode_num"] >= kwargs["upload_num"]:
            where_cond = ["upload_num>=%s" % kwargs["upload_num"]]
            update_value["upload_num"] = kwargs["upload_num"]
            print("gg")
            l = self._update_info(video_type, video_no, where_cond=where_cond, **update_value)
            if l > 0:
                self.delete_episode(video_no, episode_index=kwargs["upload_num"], delete_mode="multi")
        else:
            l = self._update_info(video_type, video_no, **update_value)
        return l

    def update_episode(self, video_no, episode_index, title=None, episode_url=None, episode_pic=None):
        where_value = dict(video_no=video_no, episode_index=episode_index)
        kwargs = dict(title=title, episode_pic=episode_pic, episode_url=episode_url)
        l = self.db.execute_update(self.t_episode, update_value=kwargs, where_value=where_value)
        return l

    def select_video(self, video_type, video_no=None):
        where_value = dict()
        where_cond = ["status<>0"]
        if video_type is not None:
            where_value = dict(video_type=video_type)
            if video_no is not None:
                where_value["video_no"] = video_no
        cols = ["video_type", "video_no", "video_name", "video_desc", "episode_num", "adder", "status",
                "video_extend", "video_pic", "insert_time", "upload_num", "listen_num", "accept_formats",
                "link_people"]
        items = self.db.execute_select(self.t_info, cols=cols, where_value=where_value, where_cond=where_cond)
        for item in items:
            if item["video_extend"] is not None:
                item.update(json.loads(item["video_extend"]))
                del item["video_extend"]
        return items

    def select_multi_video(self, video_type, multi_no):
        multi_no = filter(lambda x: re.match("^[a-z0-9A-Z]{32}$", x), multi_no)
        if len(multi_no) <= 0:
            return []
        where_value = dict(video_type=video_type)
        where_cond = ["status<>0", "video_no in ('%s')" % "','".join(multi_no)]
        cols = ["video_type", "video_no", "video_name", "video_desc", "episode_num", "adder", "status",
                "video_extend", "video_pic", "insert_time", "upload_num", "listen_num", "accept_formats",
                "link_people"]
        items = self.db.execute_select(self.t_info, cols=cols, where_value=where_value, where_cond=where_cond)
        for item in items:
            if item["video_extend"] is not None:
                item.update(json.loads(item["video_extend"]))
                del item["video_extend"]
        return items

    def select_episode(self, video_no):
        where_value = dict(video_no=video_no)
        cols = ["video_no", "episode_index", "title", "episode_url", "episode_pic", "listen_num"]
        items = self.db.execute_select(self.t_episode, cols=cols, where_value=where_value)
        return items

    def add_record(self, video_type, video_no, episode_index):
        r = self._update_listen_num(video_type, video_no, episode_index)
        return r

    def online_video(self, video_no):
        l = self._update_status(video_no, add_status=64)
        return l

    def delete_video(self, video_type, video_no):
        l = self._update_info(video_type, video_no, status=0)
        return l

    def delete_episode(self, video_no, episode_index, delete_mode="single"):
        where_value = dict(video_no=video_no)
        where_cond = []
        if delete_mode == "single":
            where_value["episode_index"] = episode_index
        else:
            where_cond = ["episode_index>%s" % episode_index]
        l = self.db.execute_delete(self.t_episode, where_value=where_value, where_cond=where_cond)
        return l
# !/usr/bin/env python
# coding: utf-8

from wildzh.classes import BaseObject
from wildzh.db.models import video

__author__ = 'zhouhenglc'


class Video(BaseObject):
    model = video.VideoModel
    uuid_col = 'video_uuid'

    def new(self, session, title, desc, state, user_no, ):
        pass

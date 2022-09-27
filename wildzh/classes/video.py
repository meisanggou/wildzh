# !/usr/bin/env python
# coding: utf-8

from wildzh.classes import BaseObject
from wildzh.db.models import video

__author__ = 'zhouhenglc'


class Video(BaseObject):
    model = video.VideoModel
    uuid_col = 'video_uuid'

    def new(self, session, video_title, video_desc, video_state,
            video_location, user_no):
        kwargs = {'video_title': video_title, 'video_desc': video_desc,
                  'video_state': video_state, 'video_location': video_location,
                  'uploader': user_no}
        return self.create(session, **kwargs)


class VideoExamMap(BaseObject):
    model = video.VideoExamMapModel

    def new(self, session, exam_no, video_uuid, position,
            video_subject=None, video_chapter=None):
        kwargs = {}

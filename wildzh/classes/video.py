# !/usr/bin/env python
# coding: utf-8
from functools import cmp_to_key
from sqlalchemy.exc import IntegrityError

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
        kwargs = {'exam_no': exam_no, 'video_uuid': video_uuid,
                  'position': position, 'video_subject': video_subject,
                  'video_chapter': video_chapter}
        try:
            obj = self.create(session, **kwargs)
        except IntegrityError as ie:
            objs = self.get_all(session, exam_no=exam_no,
                                video_uuid=video_uuid)
            if objs:
                return objs[0]
            raise ie
        return obj

    def set(self, session, exam_no, video_uuid, **kwargs):
        where_value = {'exam_no': exam_no, 'video_uuid': video_uuid}
        return self.update(session, where_value, **kwargs)

    @staticmethod
    def _cmp(v1, v2):
        # 对比 按照 exam_no position video_uuid
        if v1['exam_no'] > v2['exam_no']:
            return 1
        if v1['exam_no'] < v2['exam_no']:
            return -1
        if v1['position'] > v2['position']:
            return 1
        if v1['position'] < v2['position']:
            return -1
        if v1['video_uuid'] > v2['video_uuid']:
            return 1
        if v1['video_uuid'] < v2['video_uuid']:
            return -1
        return 0

    def get_items(self, session, **kwargs):
        query = session.query(self.model).filter_by(**kwargs).join(
            video.VideoModel,
            video.VideoModel.video_uuid==self.model.video_uuid
        ).add_entity(video.VideoModel)
        _items = query.all()
        items = []
        for _item in _items:
            value = {}
            for _o in _item:
                value.update(**_o.to_dict())
            items.append(value)
        items.sort(key=cmp_to_key(self._cmp))

        return items


class VideoProgress(BaseObject):
    model = video.VideoProgressModel

    def new(self, session, video_uuid, user_no, play_seconds):
        kwargs = {'video_uuid': video_uuid, 'user_no': user_no,
                  'play_seconds': play_seconds}
        self.create(session, **kwargs)

    def set(self, session, video_uuid, user_no, play_seconds):
        where_value = {'video_uuid': video_uuid, 'user_no': user_no}
        n = self.update(session, where_value, play_seconds=play_seconds)
        if n <= 0:
            self.new(session, video_uuid, user_no, play_seconds)

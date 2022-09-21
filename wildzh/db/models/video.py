# !/usr/bin/env python
# coding: utf-8
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class VideoModel(Base):

    __tablename__ = 'video'

    video_uuid = sqlalchemy.Column(sqlalchemy.VARCHAR(36), primary_key=True)
    video_title = sqlalchemy.Column(sqlalchemy.VARCHAR(100))
    video_desc = sqlalchemy.Column(sqlalchemy.VARCHAR(255))
    video_state = sqlalchemy.Column(sqlalchemy.INT())
    video_location = sqlalchemy.Column(sqlalchemy.VARCHAR(255))
    uploader = sqlalchemy.Column(sqlalchemy.INT())
    add_time = sqlalchemy.Column(sqlalchemy.INT())
    update_time = sqlalchemy.Column(sqlalchemy.INT())

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


class VideoExamMapModel(Base):

    __tablename__ = 'video_exam_map'

    exam_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    video_uuid = sqlalchemy.Column(sqlalchemy.VARCHAR(36), primary_key=True)

    video_subject = sqlalchemy.Column(sqlalchemy.INT(), nullable=True)
    video_chapter = sqlalchemy.Column(sqlalchemy.VARCHAR(35),
                                         nullable=True)
    position = sqlalchemy.Column(sqlalchemy.INT())
    add_time = sqlalchemy.Column(sqlalchemy.INT())
    update_time = sqlalchemy.Column(sqlalchemy.INT())

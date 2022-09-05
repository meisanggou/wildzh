# !/usr/bin/env python
# coding: utf-8
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class VideoModel(Base):

    __tablename__ = 'video'

    video_uuid = sqlalchemy.Column(sqlalchemy.VARCHAR(36), primary_key=True)

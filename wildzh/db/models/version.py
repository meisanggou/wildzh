# !/usr/bin/env python
# coding: utf-8
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class VersionMPModel(Base):

    __tablename__ = 'version_mp'

    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    version = sqlalchemy.Column(sqlalchemy.VARCHAR())
    max_version = sqlalchemy.Column(sqlalchemy.VARCHAR())
    min_version = sqlalchemy.Column(sqlalchemy.VARCHAR())
    last_modify = sqlalchemy.Column(sqlalchemy.VARCHAR())

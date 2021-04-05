# !/usr/bin/env python
# coding: utf-8
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class UserModel(Base):
    __tablename__ = 'sys_user'

    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True,
                                autoincrement=True)
    user_name = sqlalchemy.Column(sqlalchemy.VARCHAR(22), unique=True)
    password = sqlalchemy.Column(sqlalchemy.VARCHAR(255))
    role = sqlalchemy.Column(sqlalchemy.INT())
    nick_name = sqlalchemy.Column(sqlalchemy.VARCHAR(100))
    wx_id = sqlalchemy.Column(sqlalchemy.CHAR(28), unique=True)
    creator = sqlalchemy.Column(sqlalchemy.VARCHAR(22))
    email = sqlalchemy.Column(sqlalchemy.VARCHAR(100), unique=True)
    tel = sqlalchemy.Column(sqlalchemy.VARCHAR(11), unique=True)
    avatar_url = sqlalchemy.Column(sqlalchemy.VARCHAR(200))
    add_time = sqlalchemy.Column(sqlalchemy.INT())

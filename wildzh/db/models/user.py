# !/usr/bin/env python
# coding: utf-8
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class UserModel(Base):
    __tablename__ = 'sys_user'

    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True,
                                autoincrement=True)
    user_name = sqlalchemy.Column(sqlalchemy.String(22), unique=True)
    password = sqlalchemy.Column(sqlalchemy.String(255))
    role = sqlalchemy.Column(sqlalchemy.INT())
    nick_name = sqlalchemy.Column(sqlalchemy.String(100))
    wx_id = sqlalchemy.Column(sqlalchemy.String(28), unique=True)
    creator = sqlalchemy.Column(sqlalchemy.String(22))
    email = sqlalchemy.Column(sqlalchemy.String(100), unique=True)
    tel = sqlalchemy.Column(sqlalchemy.String(11), unique=True)
    avatar_url = sqlalchemy.Column(sqlalchemy.String(200))
    add_time = sqlalchemy.Column(sqlalchemy.INT())

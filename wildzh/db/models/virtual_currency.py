# !/usr/bin/env python
# coding: utf-8
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class VCUserStatusModel(Base):

    __tablename__ = 'vc_user_status'

    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    balance = sqlalchemy.Column(sqlalchemy.INT(), default=0)
    expenses = sqlalchemy.Column(sqlalchemy.INT(), default=0)
    credit_line = sqlalchemy.Column(sqlalchemy.INT(), default=0)
    sys_balance = sqlalchemy.Column(sqlalchemy.INT(), default=0)
    sys_expenses = sqlalchemy.Column(sqlalchemy.INT(), default=0)
    update_time = sqlalchemy.Column(sqlalchemy.INT())

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


class VCGiveFreqModel(Base):

    __tablename__ = 'vc_give_frequency'

    give_type = sqlalchemy.Column(sqlalchemy.VARCHAR(20), primary_key=True)
    give_id = sqlalchemy.Column(sqlalchemy.VARCHAR(100), default="")
    freq = sqlalchemy.Column(sqlalchemy.INT(), default=1)
    last_id = sqlalchemy.Column(sqlalchemy.VARCHAR(50), default="")
    first_time = sqlalchemy.Column(sqlalchemy.INT())


class VCUserBillingModel(Base):

    __table_name = 'vc_user_billing'



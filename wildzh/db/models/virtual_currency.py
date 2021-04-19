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
    give_id = sqlalchemy.Column(sqlalchemy.VARCHAR(100), default="",
                                primary_key=True)
    freq = sqlalchemy.Column(sqlalchemy.INT(), default=1)
    last_id = sqlalchemy.Column(sqlalchemy.VARCHAR(50), default="")
    first_time = sqlalchemy.Column(sqlalchemy.INT())


class VCUserBillingModel(Base):

    __tablename__ = 'vc_user_billing'

    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    billing_no = sqlalchemy.Column(sqlalchemy.BIGINT(), primary_key=True)
    add_time = sqlalchemy.Column(sqlalchemy.INT())
    billing_project = sqlalchemy.Column(sqlalchemy.INT())
    project_name = sqlalchemy.Column(sqlalchemy.VARCHAR(30))
    amount = sqlalchemy.Column(sqlalchemy.INT())
    detail = sqlalchemy.Column(sqlalchemy.VARCHAR(30), comment="")
    remark = sqlalchemy.Column(sqlalchemy.VARCHAR(200), comment="")
    status = sqlalchemy.Column(sqlalchemy.SMALLINT())
    is_delete = sqlalchemy.Column(sqlalchemy.BOOLEAN(), default=False)

# !/usr/bin/env python
# coding: utf-8
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class SecurityCaptureScreenModel(Base):

    __tablename__ = 'security_capture_screen'

    period_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    num = sqlalchemy.Column(sqlalchemy.INT())
    update_time = sqlalchemy.Column(sqlalchemy.INT(), comment="")

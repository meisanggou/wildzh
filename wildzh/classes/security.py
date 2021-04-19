# !/usr/bin/env python
# coding: utf-8

from wildzh.classes import BaseObject
from wildzh.db.models import security
from wildzh.utils import datetime_helper

__author__ = 'zhouhenglc'


class SecurityCaptureScreen(BaseObject):

    model = security.SecurityCaptureScreenModel

    def get(self, session, user_no):
        period_no = datetime_helper.calc_day_period_no()
        exists = self.get_all(session, period_no=period_no, user_no=user_no)
        if not exists:
            obj = self.model(period_no=period_no, user_no=user_no, num=0,
                             update_time=self.now_time)
            obj.save(session)
            return obj
        return exists[0]

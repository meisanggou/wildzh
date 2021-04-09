# !/usr/bin/env python
# coding: utf-8
from wildzh.classes import BaseObject
from wildzh.db.models import virtual_currency as vc_model


__author__ = 'zhouhenglc'


class VCUserStatus(BaseObject):
    model = vc_model.VCUserStatusModel

    def create(self, session, user_no):
        kwargs = {'user_no': user_no, 'update_time': self.now_time}
        return super().create(session, **kwargs)

    def get(self, session, user_no):
        exists = self.get_all(session, user_no=user_no)
        if not exists:
            instance = self.create(session, user_no)
        else:
            instance = exists[0]
        return instance.to_dict()

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


class VCGiveFreq(BaseObject):
    model = vc_model.VCGiveFreqModel

    def get(self, session, give_type, give_id):
        exists = self.get_all(session, give_type=give_type, give_id=give_id)
        if exists:
            return exists[0]
        obj = self.model(give_type=give_type, give_id=give_id, freq=0,
                         first_time=self.now_time)
        obj.save(session)
        return obj

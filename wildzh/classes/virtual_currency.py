# !/usr/bin/env python
# coding: utf-8
import time

from wildzh.classes import BaseObject
from wildzh.db.models import virtual_currency as vc_model


__author__ = 'zhouhenglc'


class VCUserStatus(BaseObject):
    model = vc_model.VCUserStatusModel

    def new(self, session, user_no):
        kwargs = {'user_no': user_no, 'update_time': self.now_time}
        return super().create(session, **kwargs)

    def get_obj(self, session, user_no):
        exists = self.get_all(session, user_no=user_no)
        if not exists:
            instance = self.new(session, user_no)
        else:
            instance = exists[0]
        return instance

    def get(self, session, user_no):
        instance = self.get_obj(session, user_no)
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


class VCUserBilling(BaseObject):
    model = vc_model.VCUserBillingModel

    def gen_no(self, user_no):
        now = int(self.now_time * 100)
        _base = 100000
        no =  now * _base +  (user_no % _base)
        return no

    def new(self, session, user_no, billing_project, project_name,
               amount, detail, remark, status):
        billing_no = self.gen_no(user_no)
        add_time = self.now_time
        kwargs = {'user_no': user_no, 'billing_no': billing_no,
                  'add_time': add_time, 'billing_project': billing_project,
                  'project_name': project_name, 'amount': amount,
                  'detail': detail, 'remark': remark, 'status': status}
        return self.create(session, **kwargs)

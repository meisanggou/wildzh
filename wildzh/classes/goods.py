# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


class GoodConditionResult(object):

    def __init__(self, enable, next_condition=None):
        self.enable = enable
        self.next_condition = next_condition


class GoodVCCond(object):

    def __init__(self, max_num=None, good_type=None, good_id=None):
        self.max_num = max_num
        self.good_type = good_type
        self.good_id = good_id


class GoodExchangeResult(object):

    def __init__(self, result, message=None, vc_count=None,
                 billing_project=None, project_name=None, detail=None,
                 remark=None):
        self.result = result
        self.message = message
        self.vc_count = vc_count
        self.billing_project = billing_project
        self.project_name = project_name
        self.detail = detail
        self.remark = remark

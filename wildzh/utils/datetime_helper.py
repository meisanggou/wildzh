# !/usr/bin/env python
# coding: utf-8
import datetime

__author__ = 'zhouhenglc'


DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_E = '%Y%m%d'

def datetime_str(dt):
    return dt.strftime(DATE_FORMAT_E)


def now_datetime_str():
    return datetime_str(datetime.datetime.now())

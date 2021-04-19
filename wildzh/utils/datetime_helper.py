# !/usr/bin/env python
# coding: utf-8
import datetime
import time

__author__ = 'zhouhenglc'


DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_E = '%Y%m%d'
BASIC_PT = 1578240000  # 2020-01-06 00:00:00 Monday
ONE_DAY_PERIOD = 24 * 60 * 60
ONE_WEEK_PERIOD = 7 * ONE_DAY_PERIOD


def datetime_str(dt):
    return dt.strftime(DATE_FORMAT_E)


def now_datetime_str():
    return datetime_str(datetime.datetime.now())


def calc_week_period_no(t=None):
    if not t:
        t = time.time()
    period_no = (t - BASIC_PT) / ONE_WEEK_PERIOD
    return int(period_no)


def calc_day_period_no(t=None):
    if not t:
        t = time.time()
    period_no = (t - BASIC_PT) / ONE_DAY_PERIOD
    return int(period_no)

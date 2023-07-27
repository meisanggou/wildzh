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


def get_month_days(year, month):
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month in (4, 6, 9, 11):
        return 30
    if year % 100 == 0:
        if year % 400 == 0:
            return 29
        return 28
    elif year % 4 == 0:
        return 29
    return 28


def calc_ymd(dt1, dt2):
    v1 = '%s%02d%02d%02d%02d%02d' % (dt1.year, dt1.month, dt1.day, dt1.hour,
                                     dt1.minute, dt1.second)
    v2 = '%s%02d%02d%02d%02d%02d' % (dt2.year, dt2.month, dt2.day, dt2.hour,
                                     dt2.minute, dt2.second)
    v1 = int(v1)
    v2 = int(v2)
    offset = int((v1 - v2) / 1000000)
    year = int(offset / 10000)
    offset %= 10000
    month = int(offset / 100)
    offset %= 100
    if month > 12:
        month = (month + 12) % 100
    day = offset
    if day > 31:
        day = (day + get_month_days(dt2.year, dt2.month)) % 100
    interval = {'year': year, 'month': month, 'day': day}
    delta = dt1 - dt2
    dur = {'total_days': delta.days, 'total_seconds': delta.total_seconds()}
    dur['interval'] = interval
    return dur

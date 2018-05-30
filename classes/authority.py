# !/usr/bin/env python
# coding: utf-8

from functools import wraps

__author__ = 'meisa'


def right_authority(role_key):
    def _right_authority(f):
        @wraps(f)
        def dec(*args, **kwargs):
            print(role_key)
            return f(*args, **kwargs)
        return dec
    return _right_authority


class AuthorityDesc(object):

    _desc = []

    def __init__(self):
        pass

    @staticmethod
    def add_desc(key, value, desc):
        pass
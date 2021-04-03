# !/usr/bin/env python
# coding: utf-8
from flask import g

from flask_helper.flask_hook import FlaskHook

__author__ = 'zhouhenglc'


class AdminHook(FlaskHook):
    priority = 210

    def before_request(self):
        if (g.user_role & 2) == 2:
            g.is_admin = True
        else:
            g.is_admin = False

# !/usr/bin/env python
# coding: utf-8
from flask import g, request

from flask_login import current_user

from flask_helper.flask_hook import FlaskHook
from wildzh.db.session import get_session

__author__ = 'zhouhenglc'


class UserHook(FlaskHook):
    priority = 200

    def before_request(self):
        if current_user.is_authenticated:
            g.user_role = current_user.role
            g.user_no = current_user.user_no
            self.log.info('receive request: user:%s role:%s method:%s full_path:%s',
                     g.user_no, g.user_role, request.method, request.full_path)
        else:
            g.user_role = 0
            g.user_no = None

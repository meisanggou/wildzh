# !/usr/bin/env python
# coding: utf-8
from flask import g, request
from flask_login import current_user

from flask_helper.flask_hook import FlaskHook

from wildzh.web02 import registry



__author__ = 'zhouhenglc'


class TokenHook(FlaskHook):
    priority = 210

    def __init__(self, app):
        FlaskHook.__init__(self, app)
        self.auth_header = 'X-OAuth-Token'

    def before_request(self):
        if g.user_no is not None:
            return
        auth_data = request.headers.get(self.auth_header)
        if auth_data is None:
            return
        registry.notify('hook', 'verify_token', self, token=auth_data)

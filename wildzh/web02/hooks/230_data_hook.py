# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask import request

from flask_helper.flask_hook import FlaskHook


__author__ = 'zhouhenglc'


class RequestDataHook(FlaskHook):
    priority = 230

    def before_request(self):
        if request.method == "GET":
            return
        if 'Content-Type' not in request.headers:
            return
        content_type = request.headers['Content-Type']
        if content_type.find('application/json') >= 0:
            g.request_data = request.json
        else:
            g.request_data = {}

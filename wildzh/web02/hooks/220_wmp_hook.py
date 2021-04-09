# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask import request

from flask_helper.flask_hook import FlaskHook

from wildzh.classes.version import VersionMP
from wildzh.db.session import use_session

__author__ = 'zhouhenglc'


class WMPHook(FlaskHook):
    priority = 220
    vmp_man = VersionMP()

    def before_request(self):
        h_key = 'X-VMP-Version-N'
        if not g.user_no:
            return
        if h_key not in request.headers:
            return

        version = request.headers[h_key]
        with use_session() as session:
            self.vmp_man.update_version(session, g.user_no, version)

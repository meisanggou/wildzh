# !/usr/bin/env python
# coding: utf-8

import os
import ConfigParser
import requests
from functools import wraps

__author__ = 'meisa'

url = "https://api.weixin.qq.com/sns/jscode2session"


class MiniProgram(object):

    def __init__(self, app_id=None, app_secret=None, conf_path=None, section=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.conf_path = conf_path
        self.conf_section = section
        self.init_conf()

    def init_conf(self):
        if self.conf_path is None:
            return
        if os.path.exists(self.conf_path) is False:
            return
        if self.conf_section is None:
            return
        config = ConfigParser.ConfigParser()
        config.read(self.conf_path)
        if config.has_section(self.conf_section) is False:
            return
        if self.app_id is None and config.has_option(self.conf_section, "app_id"):
            self.app_id = config.get(self.conf_section, "app_id")
        if self.app_secret is None and config.has_option(self.conf_section, "app_secret"):
            self.app_secret = config.get(self.conf_section, "app_secret")

    def _ready_run(self, ):
        if self.app_id is None:
            raise RuntimeError("Please set app_id")
        if self.app_secret is None:
            raise RuntimeError("Please set app_secret")

    def code2session(self, code):
        self._ready_run()
        args = dict(appid=self.app_id, secret=self.app_secret, js_code=code, grant_type="authorization_code")
        resp = requests.get(url, params=args)
        print(resp.request.url)
        if resp.status_code != 200:
            return False, resp.status_code
        r_data = resp.json()
        if "errcode" in r_data:
            return False, r_data["errmsg"]
        if "openid" not in r_data:
            return False, "no openid"
        if "session_key" not in r_data:
            return False, "no session key"
        return True, resp.json()




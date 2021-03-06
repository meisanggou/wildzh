# !/usr/bin/env python
# coding: utf-8

import os
import datetime
import ConfigParser
import requests
from functools import wraps

__author__ = 'meisa'

url = "https://api.weixin.qq.com/sns/jscode2session"


class MiniProgram(object):

    _token = dict()
    token_error_code = [41001, 40001, 42001, 40014, 42007]
    wx_api_endpoint = "https://api.weixin.qq.com"

    def __init__(self, app_id=None, app_secret=None, conf_path=None, section=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.conf_path = conf_path
        self.conf_section = section
        self.init_conf()
        # self.refresh_token()

    @staticmethod
    def _request(method, url, **kwargs):
        # kwargs["verify"] = False
        return requests.request(method, url, **kwargs)

    @property
    def access_token(self):
        return MiniProgram._token[self.app_id]

    @access_token.setter
    def access_token(self, v):
        MiniProgram._token[self.app_id] = v

    def _request_tencent(self, url, method, freq=0, **kwargs):
        access_token = kwargs.pop("access_token", self.access_token)
        request_url = url % {"access_token": access_token}
        request_url = "%s%s" % (self.wx_api_endpoint, request_url)
        res = self._request(method, request_url, **kwargs)
        if res.status_code != 200:
            if freq > 2:
                return False, res.status_code
            return self._request_tencent(url, method, freq+1, **kwargs)
        r = res.json()
        if "errcode" in r:
            error_code = r["errcode"]
            if error_code == 0:
                return True, r
            if error_code in self.token_error_code:
                self.refresh_token()
                if freq > 2:
                    return False, r
                return self._request_tencent(url, method, freq+1, **kwargs)
            else:
                return False, r
        return True, r

    def refresh_token(self, freq=0):
        if freq >= 5:
            return ""
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" \
              % (self.app_id, self.app_secret)
        res = self._request("GET", url)
        if res.status_code == 200:
            r = res.json()
            print(r)
            if "access_token" in r:
                self.access_token = r["access_token"]
                # self.expires_time = datetime.datetime.now() + datetime.timedelta(seconds=r["expires_in"])
                return self.access_token
        elif res.status_code / 100 == 5:
            return self.refresh_token(freq + 1)
        else:
            return ""

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

    def wx_code(self, path, width=430):
        url = "/wxa/getwxacode?access_token=%(access_token)s"
        data = dict(path=path, width=width)
        return self._request_tencent(url, "POST", json=data)

if __name__ == "__main__":
    from zh_config import min_program_conf
    mp = MiniProgram(conf_path=min_program_conf)
    print(mp.wx_code("pages/index/index"))
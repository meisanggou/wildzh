# !/usr/bin/env python
# coding: utf-8
import binascii
import configparser
import datetime
import hashlib
import os
import requests


__author__ = 'meisa'

url = "https://api.weixin.qq.com/sns/jscode2session"


class WxSign(object):
    def __init__(self, token):
        self.token = token

    def get_sha_value(self, timestamp, nonce, encrypt=None):
        temp_arr = [self.token, timestamp, nonce]
        if encrypt is not None:
            temp_arr.append(encrypt)
        temp_arr.sort()
        temp_str = "".join(temp_arr)
        temp_sha1 = binascii.b2a_hex(hashlib.sha1(temp_str).digest())
        return temp_sha1

    def check_signature(self, signature, timestamp, nonce):
        temp_sha1 = self.get_sha_value(timestamp, nonce)
        if temp_sha1 == signature:
            return True
        else:
            return False


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
        if self.app_id not in MiniProgram._token:
            self.refresh_token()
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
        config = configparser.ConfigParser()
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
        res = self._request_tencent(url, "POST", json=data)
        return res

    def send_message(self, to_user, template_id, page, data):
        url = '/cgi-bin/message/subscribe/send?access_token=%(access_token)s'
        r_data = {'touser': to_user, 'template_id': template_id,
                  'page': page, 'data': data}
        res = self._request_tencent(url, 'POST', json=r_data)
        return res

    def send_fb_message(self, to_user, exam_no, exam_name, fb_type, question_no, desc):
        template_id = 'BvdlC-Wv_oTNseRF8xSu_5B-r2dxv5GIbApYLgqoHMw'
        page = '/pages/exam/exam_fb?examNo=%s' % exam_no
        data = {'thing1': {'value': exam_name}, 'thing2': {'value': fb_type},
                'number3': {'value': question_no}, 'thing4': {'value': desc}}
        return self.send_message(to_user, template_id, page, data)


if __name__ == "__main__":
    from zh_config import min_program_conf
    print(min_program_conf)
    mp = MiniProgram(conf_path=min_program_conf, section='01')
    r = mp.send_fb_message('oorDD5AfcJvKLrzQRyyxIdrNoSGo', '2020-06-08 19:38:00', 'Hello World!')
    print(r)
    # print(mp.wx_code("pages/index/index"))
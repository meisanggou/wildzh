# !/usr/bin/env python
# coding: utf-8

import base64
from datetime import datetime, timedelta, date
import hmac
import json
import random

from wildzh.utils.constants import TIME_FORMAT


__author__ = 'zhouhenglc'

# common function start
dict_key = "Mwd Oauth 2Sliw335s\t&G"
hmac_key = "wild\n AccEss ToKen\t"
refresh_hmac_key = "R \t geneac ToKEN"
basic_date = date(year=2020, month=8, day=27)

access_token_timeout = 7200
dict_token_timeout = 3600
refresh_token_timeout = access_token_timeout * 100

def hmac_info(key, s):
    return hmac.new(key, s).digest()


def generate_token(user_name, scope, grant_type, refresh_token=None):
    # 生成access_token
    expires_in = datetime.now() + timedelta(seconds=access_token_timeout)
    salt = random.random()
    token_info = {"expires_in": expires_in.strftime(TIME_FORMAT),
                  "salt": salt, "user_name": user_name,
                  "scope": scope, "grant_type": grant_type,
                  "timestamp": calc_timestamp()}
    str_token_info = json.dumps(token_info)
    hmac_token_info = hmac_info(hmac_key, str_token_info)
    access_token = base64.b64encode(hmac_token_info + str_token_info)
    # 生成refresh_token
    if refresh_token is None:
        refresh_expires_in = datetime.now() + timedelta(seconds=refresh_token_timeout)
        refresh_token_info = {
            "expires_in": refresh_expires_in.strftime(TIME_FORMAT),
            "salt": salt, "user_name": user_name, "scope": scope,
            "grant_type": grant_type, "refresh": True,
            "timestamp": calc_timestamp()}
        str_refresh_info = json.dumps(refresh_token_info)
        hmac_refresh_info = hmac_info(refresh_hmac_key, str_refresh_info)
        refresh_token = base64.b64encode(hmac_refresh_info + str_refresh_info)
    data = {"access_token": access_token,
            "expires_in": access_token_timeout,
            "scope": scope,
            "refresh_token": refresh_token,
            "user_name": user_name}
    return True, data


def analysis_token(access_token):
    try:
        info = base64.b64decode(access_token)
        str_token_info = info[16:]
        hmac_token_info = hmac_info(hmac_key, str_token_info)
        if hmac_token_info != info[:16]:
            return False, ""
        token_info = json.loads(str_token_info)
        if "expires_in" not in token_info:
            return False, ""
        if datetime.strptime(token_info["expires_in"], TIME_FORMAT) < datetime.now():
            return False, ""
        return True, token_info
    except Exception as e:
        error_message = "%s TOKEN ANALYSIS ERROR %s" % (datetime.now().strftime(TIME_FORMAT), str(e.args))
        print(error_message)
        return False, ""


def analysis_refresh_token(refresh_token):
    try:
        info = base64.b64decode(refresh_token)
        str_refresh_info = info[16:]
        hmac_refresh_info = hmac_info(refresh_hmac_key, str_refresh_info)
        if hmac_refresh_info != info[:16]:
            return False, ""
        refresh_info = json.loads(str_refresh_info)
        if "expires_in" not in refresh_info:
            return False, ""
        if "refresh" not in refresh_info:
            return False, ""
        if refresh_info["refresh"] is not True:
            return False, ""
        if datetime.strptime(refresh_info["expires_in"], TIME_FORMAT) < datetime.now():
            return False, ""
        return True, refresh_info
    except Exception as e:
        error_message = "%s REFRESH ANALYSIS ERROR %s" % (datetime.now().strftime(TIME_FORMAT), str(e.args))
        print(error_message)
        return False, ""


def calc_timestamp(dt=None, sdt=None):
    if dt is not None:
        return (dt.date() - basic_date).days
    if sdt is not None:
        dt = datetime.strptime(sdt, TIME_FORMAT)
        return (dt.date() - basic_date).days
    return (date.today() - basic_date).days

# common function end


class UserToken(object):

    def gen_token(self):
        pass


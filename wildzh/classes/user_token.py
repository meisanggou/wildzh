# !/usr/bin/env python
# coding: utf-8

import base64
from datetime import datetime, timedelta, date
import hmac
import json
import random
import time

from mysqldb_rich.db2 import DB

from wildzh.utils import constants
from wildzh.utils import registry


__author__ = 'zhouhenglc'

# common function start
dict_key = "Mwd Oauth 2Sliw335s\t&G"
hmac_key = "wild\n AccEss ToKen\t"
refresh_hmac_key = "R \t geneac ToKEN"
basic_date = date(year=2020, month=8, day=27)

access_token_timeout = 7200
dict_token_timeout = 3600
refresh_token_timeout = access_token_timeout * 100
ENCODING = constants.ENCODING
TIME_FORMAT = constants.TIME_FORMAT


def hmac_info(key, s):
    if isinstance(key, str):
        key = bytearray(key, encoding=ENCODING)
    hc = hmac.new(key, digestmod='sha256')
    if isinstance(s, str):
        s = s.encode(ENCODING)
    hc.update(s)
    return hc.digest()


def generate_token(user_no, scope, grant_type, refresh_token=None,
                   timeout=None, extra_data=None):
    # 生成access_token
    if not timeout:
        timeout = access_token_timeout
    refresh_timeout = timeout * 100
    expires_in = datetime.now() + timedelta(seconds=timeout)
    salt = random.random()
    token_info = {"expires_in": expires_in.strftime(TIME_FORMAT),
                  "salt": salt, "user_no": user_no,
                  "scope": scope, "grant_type": grant_type,
                  "timestamp": calc_timestamp(),
                  "extra_data": extra_data}
    str_token_info = json.dumps(token_info)
    hmac_token_info = hmac_info(hmac_key, str_token_info)
    access_token = base64.b64encode(hmac_token_info +
                                    str_token_info.encode(ENCODING))
    # 生成refresh_token
    if refresh_token is None:
        refresh_expires_in = datetime.now() + timedelta(seconds=refresh_timeout)
        refresh_token_info = {
            "expires_in": refresh_expires_in.strftime(constants.TIME_FORMAT),
            "salt": salt, "user_no": user_no, "scope": scope,
            "grant_type": grant_type, "refresh": True,
            "timestamp": calc_timestamp()}
        str_refresh_info = json.dumps(refresh_token_info)
        hmac_refresh_info = hmac_info(refresh_hmac_key, str_refresh_info)
        refresh_token = base64.b64encode(hmac_refresh_info +
                                         str_refresh_info.encode(ENCODING))
    data = {"access_token": access_token.decode(ENCODING),
            "expires_in": timeout,
            "scope": scope,
            "refresh_token": refresh_token.decode(ENCODING),
            "user_no": user_no}
    return True, data


def analysis_token(access_token):
    try:
        info = base64.b64decode(access_token)
        str_token_info = info[32:]
        hmac_token_info = hmac_info(hmac_key, str_token_info)
        if hmac_token_info != info[:32]:
            return False, "failed to verify signature"
        token_info = json.loads(str_token_info)
        if "expires_in" not in token_info:
            return False, "lack expires_in"
        if datetime.strptime(token_info["expires_in"], TIME_FORMAT) < datetime.now():
            token_info['expired'] = True
        else:
            token_info['expired'] = False
        return True, token_info
    except Exception as e:
        error_message = "%s TOKEN ANALYSIS ERROR %s" % (datetime.now().strftime(TIME_FORMAT), str(e))
        print(error_message)
        return False, set(e)


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

@registry.has_registry_receivers
class UserToken(object):
    MAX_DEVICE = 1

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t_token = 'user_token'
        self.token_cols = ['user_no', 'access_token', 'identity',
                           'refresh_token', 'update_time', 'need_refresh']

    def _gen_token_admit(self, user_no, identity):
        # TODO 限制不能无限生成
        # 获得当前活跃的终端
        ## 判定申请的终端是否是活跃的终端
        ### 如果是 允许申请
        ### 如果不是 判定当前活跃终端数是否超过限制 删除申请时间靠前的终端授权
        ### 如果是新终端 判定是否以前有过授权 判定间隔时间是否够长
        max_device = self.MAX_DEVICE
        admit = False
        token_items = self.db.execute_select(
            self.t_token, where_value={'user_no': user_no})
        token_items.sort(key=lambda x: x['update_time'])
        if len(token_items) >= self.MAX_DEVICE:
            active_items = []
            inactive_items = []
            req_item = None
            for item in token_items:
                if item['identity'] == identity:
                    req_item = item
                if item['access_token']:
                    active_items.append(item)
                else:
                    inactive_items.append(item)
            if req_item and req_item['access_token']:
                # 当前申请终端 是活跃终端，可以重新申请
                admit = True
            elif len(active_items) >= max_device:
                # 当前申请终端不是活跃终端，且活跃终端，到达限制，不允许申请
                admit = False
            elif not inactive_items:
                # 当前不是活跃终端，当前活跃终端数又没超限，又没有不活跃终端，理论上不会走到该分支
                admit = True
            else:
                _t = int(time.time()) - 24 * 3600
                # 最近不活跃的一个终端，必须超过24小时
                if inactive_items[-1]['update_time'] < _t:
                    admit = True
                else:
                    admit = False
            for i in range(0, len(active_items) - self.MAX_DEVICE + 1):
                # 删除申请时间靠前的终端授权
                item = active_items[i]
                where_value = {'user_no': user_no,
                               'identity': item['identity']}
                update_value = {'access_token': None,
                                'refresh_token': None,
                                'update_time': int(time.time())}
                self.db.execute_update(
                    self.t_token, where_value=where_value,
                    update_value=update_value)
        else:
            # 当前所有终端数，少于限制，可以申请
            admit = True
        return admit

    def gen_token(self, user_no, identity, timeout, user_role):
        if not self._gen_token_admit(user_no, identity):
            return False, "登录客户端数达到限制。请确保其他客户退出登录超过24小时后，重试！"
        r, data = generate_token(user_no, '', 'password',
                                 timeout=timeout,
                                 extra_data={'user_role': user_role})
        access_token = data['access_token']
        time_stamp = int(time.time())
        db_data = {'user_no': user_no, 'access_token': access_token,
                   'update_time': time_stamp, 'identity': identity,
                   'refresh_token': data['refresh_token']}
        u_keys = ['access_token', 'refresh_token', 'update_time']
        l = self.db.execute_duplicate_insert(self.t_token, kwargs=db_data, u_keys=u_keys)
        if l <= 0:
            return False, 'internal error: gen token insert'
        return True, data

    def verify_token(self, token):
        # token:timestamp:algorithm:sign
        t_items = token.split(":")
        if len(t_items) != 4:
            return False, {'error': constants.TOKEN_BAD_FORMAT,
                           'detail': 'token should consist of four parts'}
        access_token, timestamp, algorithm, sign = t_items
        try:
            if abs(time.time() - int(timestamp)) > 10:
                return False, {'error': constants.TOKEN_BAD_FORMAT,
                           'detail': 'the request timestamp deviation '
                                     'is too large'}
        except ValueError:
            return False, {'error': constants.TOKEN_BAD_FORMAT,
                           'detail': 'the request timestamp not an integer'}
        r, _token_data = analysis_token(access_token)
        if r is False:
            return False, {'error': constants.TOKEN_BAD_FORMAT,
                           'detail': 'analysis token fail: %s' % _token_data}
        if _token_data['expired']:
            return False, {'error': constants.TOKEN_EXPIRED,
                           'detail': ''}
        where_value = dict(user_no=_token_data['user_no'],
                           access_token=access_token)
        db_items = self.db.execute_select(self.t_token, where_value,
                                          cols=self.token_cols)
        if len(db_items) <= 0:
            return False, {'error': constants.TOKEN_NOT_STORAGE,
                           'detail': ''}
        db_token = db_items[0]
        if db_token['need_refresh']:
            return False, {'error': constants.TOKEN_REQUIRE_REFRESH,
                           'detail': ''}
        # TODO verify sign
        return True, _token_data

    @registry.receive_callback('hook', 'verify_token')
    def verify_token_callback(self, resource, event ,trigger, token):
        return self.verify_token(token)


if __name__ == '__main__':
    token_data = generate_token('admin', 'api', 'password', timeout=60)
    print(token_data)
    a_data = analysis_token(token_data[1]['access_token'])
    print(a_data)


# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask import request

from zh_config import db_conf_path

from wildzh.classes.user_token import UserToken
from wildzh.web02.view import View2


__author__ = 'zhouhenglc'

url_prefix = "/user/token"
token_view = View2("token", __name__, url_prefix=url_prefix)
c_token = UserToken(db_conf_path)


@token_view.route('/password', methods=["GET", "POST"])
def gen_token():
    """
    申请
    账户名 密码 identity --> token
    验证
    token + identity + timestamp --> sign
    token + sign + timestamp --> auth
    """
    # 账户名 密码

    # token中包含user_role user_role发生改变时 删除所有token
    #
    data = request.json
    user_name = data['user_name']
    password = data['password']
    # 校验账户名和密码
    c_user = token_view.get_handler('user')
    code, item = c_user.user_confirm(g.session, password, user=user_name)
    if code != 0:
        extra_data = {'code': code}
        return {'status': False, 'data': '账户名不存在或者密码不正确',
                'extra_data': extra_data}
    # 生成token
    timeout = 365 * 24 * 60 * 60
    identity = data['identity']
    r, t_data = c_token.gen_token(item['user_no'], identity=identity,
                                  timeout=timeout, user_role=item['role'])
    print(t_data)
    return {'status': r, 'data': t_data}

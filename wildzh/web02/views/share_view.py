# !/usr/bin/env python
# coding: utf-8
import base64
from zh_config import db_conf_path

from flask import g
from wildzh.utils import constants
from wildzh.utils.log import getLogger
from wildzh.utils import registry
from wildzh.classes.share import ShareRecords
from wildzh.classes.share import ShareKey
from wildzh.web02.view import View2


__author__ = 'zhouhenglc'

LOG = getLogger()
url_prefix = "/share"

share_view = View2("share", __name__, url_prefix=url_prefix,
                     auth_required=True)
SHARE_KEY_MAN = ShareKey(db_conf_path=db_conf_path)
SHARE_RECORDS_MAN = ShareRecords(db_conf_path=db_conf_path)


@share_view.route('/token', methods=['POST'])
def gen_share_token():
    data = g.request_data
    resource = data.pop('resource', None)
    resource_id = data.pop('resource_id', None)
    share_key = SHARE_KEY_MAN.create(g.user_no)
    # token = base64(<resource>|<resource_id>|<user_no>|sign|<,join(others)>)
    result = registry.notify_callback(
        resource, constants.E_GEN_TOKEN, share_view, resource_id=resource_id,
        user_no=g.user_no, share_key=share_key, **data)
    if not result:
        return {'status': False, 'data': None}
    if 'sign' not in result or 'others' not in result:
        return {'status': False, 'data': None}
    items = {'resource': resource, 'resource_id': resource_id,
             'user_no': g.user_no, 'sign': result['sign'],
             'others': ','.join(result['others'])}
    p_token = '%(resource)s|%(resource_id)s|%(user_no)s|%(sign)s|%(others)s' \
              % items
    token = base64.b64encode(p_token.encode(constants.ENCODING)).decode(
        constants.ENCODING)
    p_data = result.get('data', {})
    p_data.update({'token': token})
    return {'status': True, 'data': p_data}


@share_view.route('/token/action', methods=['POST'])
def parsing_share_token():
    data = g.request_data
    action = data['action']  # dry-run or run
    token = data['token']
    res_data = {'status': False, 'action': 'show', 'data': ''}
    base64.b64decode(token.encode(constants.ENCODING))
    p_token = base64.b64decode(token.encode(constants.ENCODING)).decode(
        constants.ENCODING)
    items = p_token.split('|', 4)

    if len(items) != 5:
        res_data['data'] = '邀请码错误'
        LOG.warning('Share fail, token is %s, message: %s', token,
                    res_data['data'])
        return res_data
    # 是否已经接受过该邀请
    r_items = SHARE_RECORDS_MAN.select(g.user_no, share_token=token)
    if r_items:
        res_data['action'] = 'ignore'
        res_data['data'] = '已经接受该邀请'
        LOG.warning('Share fail, token is %s, message: %s', token,
                    res_data['data'])
        return res_data
    resource, resource_id, i_user_no, sign, others = items
    share_key = SHARE_KEY_MAN.select(i_user_no)
    result = registry.notify_callback(
        resource, constants.E_PARSING_TOKEN, share_view,
        resource_id=resource_id, action=action, user_no=g.user_no,
        user_role=g.user_role, share_key=share_key,
        inviter_user_no=int(i_user_no), sign=sign,
        others=others.split(','))
    res_data['status'] = result['status']
    if result['status']:
        res_data['data'] = result
        if action != 'dry-run':
            # 记录
            SHARE_RECORDS_MAN.create(g.user_no, resource, resource_id,
                                     i_user_no, token, result.get('extend'))
    else:
        res_data['action'] = result.get('action', 'show')
        LOG.warning('Share fail, token is %s, message: %s', token,
                    result['message'])
        res_data['data'] = result['message']
    return res_data

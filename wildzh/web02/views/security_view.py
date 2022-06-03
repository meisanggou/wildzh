# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask_helper.utils.registry import DATA_REGISTRY
from wildzh.classes.security import SecurityCaptureScreen
from wildzh.utils import constants
from wildzh.utils.log import getLogger
from wildzh.utils.registry import subscribe_callback

from wildzh.web02.view import View2
__author__ = 'zhouhenglc'

LOG = getLogger()
url_prefix = '/security'
security_view = View2("security", __name__, url_prefix=url_prefix,
                auth_required=True)
SE_SC_MAN = SecurityCaptureScreen()
TRUST_USERS = [8, ]


def security_firewall(resource, event, trigger, session, user_no, **kwargs):
    if user_no in TRUST_USERS:
        return None
    obj = SE_SC_MAN.get(session, user_no)
    if obj.num > 10:
        action = constants.SE_ACTION_EXIT
        message = '最近截屏次数过多，当前禁止使用，请稍后重试!'
        se = {'action': action, 'message': message}
        return se
    return None


if not DATA_REGISTRY.exist_in('registered', 'security_view'):
    subscribe_callback(security_firewall, constants.R_SE,
                       constants.E_SE_FIREWALL)
    DATA_REGISTRY.append('registered', 'security_view')


@security_view.route('/capture/screen', methods=['POST'])
def capture_screen():
    data = g.request_data
    LOG.info(data)
    times = data['times']
    obj = SE_SC_MAN.get(g.session, g.user_no)
    if times is not None:
        obj.num += times
    if obj.num <= 5 or g.user_no in TRUST_USERS:
        action = constants.SE_ACTION_NORMAL
        message = ''
    elif obj.num <= 10:
        action = constants.SE_ACTION_WARN
        message = '截屏将影响您的正常使用'
    else:
        action = constants.SE_ACTION_EXIT
        message = '最近截屏次数过多，当前禁止使用，请稍后重试'
    se = {'action': action, 'message': message}
    return {'status': True, 'data': '', 'se': se}

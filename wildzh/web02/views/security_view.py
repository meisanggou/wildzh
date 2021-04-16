# !/usr/bin/env python
# coding: utf-8
from flask import g
from wildzh.utils import constants
from wildzh.utils.log import getLogger

from wildzh.web02.view import View2
__author__ = 'zhouhenglc'

LOG = getLogger()
url_prefix = '/security'
security_view = View2("security", __name__, url_prefix=url_prefix,
                auth_required=True)


@security_view.route('/capture/screen', methods=['POST'])
def capture_screen():
    data = g.request_data
    LOG.info(data)
    times = data['times']
    action = [constants.SE_ACTION_NORMAL, constants.SE_ACTION_WARN,
              constants.SE_ACTION_EXIT][times % 3]
    se = {'action': action, 'message': ''}
    return {'status': True, 'data': '', 'se': se}

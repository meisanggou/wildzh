# !/usr/bin/env python
# coding: utf-8
from flask import g
from wildzh.utils.log import getLogger

from wildzh.classes.virtual_currency import VCUserStatus
from wildzh.web02.view import View2

__author__ = 'zhouhenglc'


LOG = getLogger()
url_prefix = "/vc"
VC_MAN = VCUserStatus()
vc_view = View2("virtual_currency", __name__, url_prefix=url_prefix,
                auth_required=True)


@vc_view.route('/status', methods=['GET'])
def get_status():
    status = VC_MAN.get(g.session, g.user_no)
    return status

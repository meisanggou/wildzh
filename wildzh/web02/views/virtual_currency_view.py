# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask_helper.utils.registry import DATA_REGISTRY
from wildzh.utils import constants
import wildzh.utils.datetime_helper as dt_helper
from wildzh.utils.log import getLogger
from wildzh.utils.registry import notify_callback
from wildzh.utils.registry import subscribe_callback

from wildzh.classes.virtual_currency import VCGiveFreq
from wildzh.classes.virtual_currency import VCUserBilling
from wildzh.classes.virtual_currency import VCUserStatus
from wildzh.web02.view import View2

__author__ = 'zhouhenglc'


LOG = getLogger()
url_prefix = "/vc"
VC_MAN = VCUserStatus()
VC_UB_MAN = VCUserBilling()
VC_GF_MAN = VCGiveFreq()

vc_view = View2("virtual_currency", __name__, url_prefix=url_prefix,
                auth_required=True)

reg_key = 'VC_GIVE'

def func_browse_ad_id(user_no, **kwargs):
    key = '%s-%s' % (user_no, dt_helper.now_datetime_str())
    return key


def func_browse_ad_check(user_no, gf_obj, **kwargs):
    max_freq = 2
    give_vc_count = 1
    last_id = None
    if gf_obj.freq >= max_freq:
        return None
    next_enable = max_freq - gf_obj.freq > 1
    cr = {'next_enable': next_enable, 'last_id': last_id,
          'give_vc_count': give_vc_count, 'billing_project': 'browse_ad',
          'project_name': '看广告得积分', 'detail': '', 'remark': '',
          'tip': '得1积分'}
    return cr


def new_billing(resource, event, trigger, session, user_no, billing_project,
                project_name, vc_count, detail, remark):
    ub_obj = VC_UB_MAN.new(session, user_no, billing_project,
                           project_name, vc_count, detail, remark, 0)
    vc_obj = VC_MAN.get_obj(session, user_no)
    vc_obj.sys_balance = vc_obj.sys_balance + vc_count
    ub_obj.status = 1
    return ub_obj, vc_obj


if not DATA_REGISTRY.exist_in('registered', 'vc_view'):
    reg_gives = DATA_REGISTRY.set_default(reg_key, {})
    reg_gives['browse_ad'] = {'id_func': func_browse_ad_id,
                              'check_func': func_browse_ad_check}

    subscribe_callback(new_billing, constants.R_VC, constants.E_NEW_BILLING)
    DATA_REGISTRY.append('registered', 'vc_view')


@vc_view.route('/status', methods=['GET'])
def get_status():
    status = VC_MAN.get(g.session, g.user_no)
    return {'status': True, 'data': status}


@vc_view.route('/give', methods=['POST'])
def give_event():
    data = g.request_data
    give_type = data['give_type']
    action = data.get('action', 'check')
    _reg_gives = DATA_REGISTRY.get(reg_key)
    if give_type not in _reg_gives:
        return {'status': False, 'data': 'give type not exist!'}
    id_func = _reg_gives[give_type]['id_func']
    give_id = id_func(g.user_no)
    gf_obj = VC_GF_MAN.get(g.session, give_type, give_id)
    check_func = _reg_gives[give_type]['check_func']
    cr = check_func(g.user_no, gf_obj)
    if not cr:
        return {'status': False, 'data': 'participation limit exceeded'}
    data = {'cr': cr}
    if action == 'run':
        ub_obj, vc_obj = notify_callback(
            constants.R_VC, constants.E_NEW_BILLING, vc_view,
            session=g.session, user_no=g.user_no,
            billing_project=cr['billing_project'],
            project_name=cr['project_name'],
            vc_count=cr['give_vc_count'], detail=cr['detail'],
            remark=cr['remark'])
        gf_obj.freq += 1
        gf_obj.last_id = cr['last_id']
        data['vc'] = vc_obj.to_dict()
    return {'status': True, 'data': data}


@vc_view.route('/give/goods', methods=['GET'])
def goods_items():
    DATA_REGISTRY.get(constants.DR_KEY_VC_GOODS, [])
    return {}

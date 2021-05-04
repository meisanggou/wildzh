# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask import request
from flask_helper.utils.registry import DATA_REGISTRY
from wildzh.utils import constants
import wildzh.utils.datetime_helper as dt_helper
from wildzh.utils.log import getLogger
from wildzh.utils.registry import notify_callback
from wildzh.utils.registry import subscribe_callback

from wildzh.classes.virtual_currency import VCGiveFreq
from wildzh.classes.virtual_currency import VCUserBilling
from wildzh.classes.virtual_currency import VCUserStatus
from wildzh.web02 import exception
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
    if vc_count < 0:
        vc_obj.consume(0 - vc_count)
    else:
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


@vc_view.route('/goods', methods=['GET'])
def goods_items():
    goods_res = DATA_REGISTRY.get(constants.DR_KEY_VC_GOODS, [])
    goods = []
    for resp_er in goods_res:
        _goods = resp_er['items'](g.session, g.user_no)
        for good in _goods:
            if 'available' not in good:
                good['available'] = 'enable'
            good['good_type'] = resp_er['good_type']
            goods.append(good)
    data = {'goods': goods}
    return {'status': True, 'data': data}


@vc_view.route('/goods/condition', methods=['GET'])
def good_required():
    args = request.args
    good_type = args['good_type']
    good_id = args['good_id']
    goods_res = DATA_REGISTRY.get(constants.DR_KEY_VC_GOODS, [])
    v = 'disable'
    for resp_er in goods_res:
        if resp_er['good_type'] == good_type:
            req_func = resp_er['condition']
            con_r = req_func(g.session, g.user_no, good_type, good_id)
            if con_r.available == 'disable':
                break
            if not con_r.next_condition:
                v = con_r.available
            else:
                vcb_items = VC_UB_MAN.get_all(
                    g.session, user_no=g.user_no,
                    billing_project=con_r.next_condition.billing_project)
                if len(vcb_items) <= con_r.next_condition.max_num:
                    v = 'enable'
    data = {'good_type': good_type, 'good_id': good_id, 'available': v}
    return {'status': True, 'data': data}


@vc_view.route('/goods/exchange', methods=['POST'])
def good_exchange():
    data = g.request_data
    LOG.info('[Important][GoodsExchange]user_no:%s, data:%s', g.user_no, data)
    good_type = data['good_type']
    good_id = data['good_id']
    goods_res = DATA_REGISTRY.get(constants.DR_KEY_VC_GOODS, [])
    for resp_er in goods_res:
        if resp_er['good_type'] == good_type:
            ec_func = resp_er['exchange']
            ec_r = ec_func(g.session, g.user_no, good_type, good_id)
            if ec_r.result is False:
                raise exception.BadRequest(description=ec_r.message)
            ub_obj, vc_obj = notify_callback(
                constants.R_VC, constants.E_NEW_BILLING, vc_view,
                session=g.session, user_no=g.user_no,
                billing_project=ec_r.billing_project,
                project_name=ec_r.project_name,
                vc_count=0 - ec_r.vc_count, detail=ec_r.detail,
                remark=ec_r.remark)
            if vc_obj.my_balance < 0:
                raise exception.BadRequest(description='积分不足')
            data = {'vc': vc_obj.to_dict(), 'message': '兑换成功'}
            return {'status': True, 'data': data}
    raise exception.BadRequest(description='商品不存在，请稍后重试')

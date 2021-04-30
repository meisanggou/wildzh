# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ENCODING = 'utf-8'


# exam status
STATUS_ONLINE = 64
STATUS_OFFLINE = 128

# token error
TOKEN_BAD_FORMAT = 'token_bad_format'  # login again
TOKEN_EXPIRED = 'token_expired'  # try refresh
TOKEN_NOT_STORAGE = 'token_not_storage'  # login again
TOKEN_REQUIRE_REFRESH = 'token_require_refresh'  # try refresh


# training question state
T_STATE_RIGHT = 'right'
T_STATE_WRONG = 'wrong'
T_STATE_SKIP = 'skip'
T_STATES = [T_STATE_RIGHT, T_STATE_WRONG, T_STATE_SKIP]


# resource constants
R_EXAM = 'exam'
R_QUESTION = 'question'
R_VC = 'virtual_currency'
R_SE = 'security'


# resource event
E_AFTER_UPDATE = 'after_update'
E_GEN_TOKEN = 'gen_token'
E_PARSING_TOKEN = 'parsing_token'
E_NEW_BILLING = 'new_billing'
E_SE_FIREWALL = 'security_firewall'


# vc billing
VB_FB = 'feedback_exam'
VB_FB_NAME = '题库问题反馈得积分'


# security handle action
SE_ACTION_NORMAL = 'normal'
SE_ACTION_WARN = 'warn'
SE_ACTION_EXIT = 'exit'


# DATA_REGISTRY keys
DR_KEY_VC_GOODS = 'vc_goods'

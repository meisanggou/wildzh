# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ENCODING = 'utf-8'


# exam  mode
# G_SELECT_MODE
# 待废弃，逐步完善使用classes.objects.question_type
# G_SELECT_MODE = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题", "多选题", "判断题"]
# G_MULTI_MODE = [6, ]  # 多选题型  多选题=6
# G_DEF_OPTIONS = [1, 6]  # 自定义选项  单选题=1 多选题=6

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
VC_EC_EM = 'vc_exchange_exam_mem'
VC_EC_EM_NAME = '积分换题库会员'


# security handle action
SE_ACTION_NORMAL = 'normal'
SE_ACTION_WARN = 'warn'
SE_ACTION_EXIT = 'exit'


# DATA_REGISTRY keys
DR_KEY_VC_GOODS = 'vc_goods'
DR_KEY_ROUTES = 'routes'


# goods type
GOOD_TYPE_EXAM = 'exam'

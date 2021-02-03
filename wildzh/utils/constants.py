# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ENCODING = 'utf-8'


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
R_QUESTION = 'question'


# resource event
E_AFTER_UPDATE = 'after_update'
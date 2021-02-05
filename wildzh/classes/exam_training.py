# !/usr/bin/env python
# coding: utf-8
import time
from mysqldb_rich.db2 import DB
from wildzh.utils import constants

__author__ = 'zhouhenglc'


"""
tag
从未对过 -- miss_num + skip_num = num
多次跳过 -- skip_num = num
全部做对 -- skip_num = miss_num = 0
从未错误 -- miss_num = 0 & num > 0
最近做对 -- last_time < 1w & last_right
最近做错 -- last_time < 1w & last_wrong
连续错误 --
最近全对 --
"""

class ExamTrainingDetail(object):
    """
    first_meet 第一次碰到该题做题状态 0做对 1做错 2直接查看答案
    first_miss 第一次做该题 是否做错
    miss_num 总共做错了该题几次
    skip_num 总共跳过该题几次
    last_meet 最近一次碰到该题做题状态
    last_miss 最近一次做该题 是否做错 1
    state_num 连续做对或者做错的次数 遇到跳过不刷新 last_miss改变时重置为0
    skip_state_num 连续跳过该题次数 遇到做对做错重置为0
    """
    state_map = {constants.T_STATE_RIGHT: 0,
                 constants.T_STATE_WRONG: 1,
                 constants.T_STATE_SKIP: 2}

    def __init__(self, db=None, db_conf_path=None):
        if db is None:
            db = DB(db_conf_path)
        self.db = db
        self.t = 'exam_training_detail'
        self.cols = ['user_no', 'exam_no', 'question_no', 'first_meet',
                     'first_miss', 'first_meet_time', 'num', 'miss_num',
                     'skip_num', 'last_meet', 'last_miss', 'last_meet_time',
                     'state_num', 'skip_state_num']

    def state_2_value(self, state):
        return self.state_map[state]

    def value_2_state(self, v):
        if not hasattr(self, '_value_2_state_map'):
            self._value_2_state_map = [constants.T_STATE_RIGHT,
                                       constants.T_STATE_WRONG,
                                       constants.T_STATE_SKIP]
        return self._value_2_state_map[v]

    def select_items(self, user_no, exam_no, question_no=None):
        where_value = dict(user_no=user_no, exam_no=exam_no)
        if question_no is not None:
            where_value['question_no'] = question_no
        items = self.db.execute_select(self.t, cols=self.cols,
                                       where_value=where_value)
        for item in items:
            item['first_meet'] = self.value_2_state(item['first_meet'])
            item['last_meet'] = self.value_2_state(item['last_meet'])
        return items

    def insert_item(self, user_no, exam_no, question_no, state):
        now_time = time.time()
        values = dict(user_no=user_no, exam_no=exam_no,
                      question_no=question_no, first_meet_time=now_time,
                      first_meet=self.state_2_value(state),
                      num=1, miss_num=0, skip_num=0, state_num=0,
                      skip_state_num=0)
        if state == constants.T_STATE_WRONG:
            values['first_miss'] = True
            values['miss_num'] = 1
            values['state_num'] = 1
        elif state == constants.T_STATE_RIGHT:
            values['first_miss'] = False
            values['state_num'] = 1
        else:
            values['first_miss'] = False
            values['skip_num'] = 1
            values['skip_state_num'] = 1
        values['last_meet'] = values['first_meet']
        values['last_miss'] = values['first_miss']
        values['last_meet_time'] = values['first_meet_time']
        l = self.db.execute_insert(self.t, kwargs=values)
        return l

    def add_detail(self, user_no, exam_no, question_no, state):
        items = self.select_items(user_no, exam_no, question_no=question_no)
        if len(items) <= 0:
            return self.insert_item(user_no, exam_no, question_no, state)
        item = items[0]
        first_answer = item['num'] == item['skip_num']
        update_values = {'num': item['num'] + 1}
        if state == constants.T_STATE_WRONG:
            if first_answer:
                update_values['first_miss'] = True
            update_values['miss_num'] = item['miss_num'] + 1
            if item['last_miss']:
                update_values['state_num'] = item['state_num'] + 1
            else:
                update_values['state_num'] = 0
            update_values['last_miss'] = True
        elif state == constants.T_STATE_RIGHT:
            if first_answer:
                update_values['first_miss'] = False
            if not item['last_miss']:
                update_values['state_num'] = item['state_num'] + 1
            else:
                update_values['state_num'] = 0
            update_values['last_miss'] = False
        else:
            update_values['skip_num'] = item['skip_num'] + 1
            if item['last_meet'] == constants.T_STATE_SKIP:
                update_values['skip_state_num'] = item['skip_state_num'] + 1
            else:
                update_values['skip_state_num'] = 0
        now_time = time.time()
        update_values['last_meet'] = self.state_2_value(state)
        update_values['last_meet_time'] = now_time
        where_value = dict(user_no=user_no, exam_no=exam_no,
                           question_no=question_no)
        l = self.db.execute_update(self.t, update_value=update_values, where_value=where_value)
        return l

    def get_tag(self,q_detail):
        pass

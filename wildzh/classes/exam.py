# !/usr/bin/env python
# coding: utf-8

import re
import time
import json
import random
import string
import uuid

from mysqldb_rich.db2 import DB
from wildzh.classes import BaseObject
from wildzh.classes.exam_feedback import ExamQuestionFeedbackObj
from wildzh.classes.objects.exam_obj import ExamObject
from wildzh.db.models import exam as exam_models
from wildzh.utils import constants

__author__ = 'meisa'

"""
题库角色exam_role
0 内部用户
1 拥有者： 所有权限
2 超级管理员：可更新题库信息 授权新的管理员
3 管理员：新增试题，更新试题 授权普通用户
5 普通成员： 可做题


10 公开题库

20 半公开题库 可查看部分题目，答案，详情
22 半公开题库 可查看部分题目，答案。不可查看详情
25 半公开题库 可查看部分题目，不可查看答案与详情




100 无任何权限
"""
"""
题库状态
1代表已录入基本信息
2代表已录入测试题目
4代表已录入结果
8 16 32
64代表已上线 对题库管理员以外的人员开放访问
128代表已下线  创建者 或者 题库管理员指定特定参数可查看
0代表已删除
"""


class ExamMemberFlow(object):
    DAY_SECONDS = 3600 * 24

    def __init__(self):
        self.t_emf = "exam_member_flow"

    def _insert_exam_member_flow(self, user_no, exam_no, update_time,
                                 exam_role, authorizer, end_time):
        data = dict(user_no=user_no, exam_no=exam_no, exam_role=exam_role,
                    authorizer=authorizer, end_time=end_time,
                    update_time=update_time)
        l = self.db.execute_insert(self.t_emf, data)
        return l

    def select_member_flows(self, user_no, exam_no):
        where_value = dict(user_no=user_no, exam_no=exam_no)
        cols = ['user_no', 'exam_no', 'exam_role', 'end_time',
                'update_time', 'authorizer']
        items = self.db.execute_select(self.t_emf, cols=cols,
                                       where_value=where_value)
        return items


class ExamMember(ExamMemberFlow):
    DAY_SECONDS = 3600 * 24

    def __init__(self):
        ExamMemberFlow.__init__(self)
        self.t_em = "exam_member"

    def _delete_exam_member(self, user_no, exam_no):
        where_value = {'user_no': user_no, 'exam_no': exam_no}
        l = self.db.execute_delete(self.t_em, where_value=where_value)
        return l

    def _insert_exam_member(self, user_no, exam_no, exam_role, authorizer,
                            end_time=None):
        data = dict(user_no=user_no, exam_no=exam_no, exam_role=exam_role,
                    authorizer=authorizer, end_time=end_time)
        data['insert_time'] = time.time()
        data['update_time'] = time.time()
        l = self.db.execute_insert(self.t_em, data)
        del data['insert_time']
        self._insert_exam_member_flow(**data)
        return l

    def _update_exam_member(self, user_no, exam_no, authorizer, end_time=None):
        where_value = dict(user_no=user_no, exam_no=exam_no)
        u_data = {'authorizer': authorizer}
        if end_time:
            u_data['end_time'] = end_time
        u_data['update_time'] = time.time()
        e_items = self._select_exam_member(user_no, exam_no)
        if len(e_items) <= 0:
            return 0
        l = self.db.execute_update(self.t_em, update_value=u_data,
                                   where_value=where_value)
        item = e_items[0]
        item.update(u_data)
        del item['insert_time']
        self._insert_exam_member_flow(**item)
        return l

    def _select_exam_member(self, user_no=None, exam_no=None, max_role=None):
        where_value = dict()
        if user_no:
            where_value['user_no'] = user_no
        if exam_no:
            where_value['exam_no'] = exam_no
        where_cond = []
        where_cond_args = []
        if max_role is not None:
            where_cond.append('exam_role <= %s')
            where_cond_args.append(max_role)
        cols = ['user_no', 'exam_no', 'exam_role', 'end_time',
                'insert_time', 'update_time']
        items = self.db.execute_select(self.t_em, cols=cols,
                                       where_value=where_value,
                                       where_cond_args=where_cond_args,
                                       where_cond=where_cond)
        return items

    def user_exams(self, user_no, exam_no=None, ensure_member=True):
        items = self._select_exam_member(user_no, exam_no)
        now_time = time.time()
        if ensure_member:
            items = [item for item in items
                     if item['end_time'] is None
                     or item['end_time'] >= now_time]
        return items

    def exam_members(self, exam_no, max_role=None):
        items = self._select_exam_member(exam_no=exam_no, max_role=max_role)
        now_time = time.time()
        items = [item for item in items
                 if item['end_time'] is None or item['end_time'] >= now_time]
        return items

    def exam_admin_members(self, exam_no):
        return self.exam_members(exam_no, 3)

    def select_user_exams(self, user_no):
        items = self.user_exams(user_no)
        e_dict = dict()
        for item in items:
            e_dict[item['exam_no']] = item
        return e_dict

    def insert_exam_member(self, user_no, exam_no, authorizer, **kwargs):
        end_time = kwargs.pop('end_time', None)
        if end_time is None:
            days = kwargs.pop('days', 0)
            if days > 0:
                end_time = time.time() + days * self.DAY_SECONDS
        return self._insert_exam_member(user_no, exam_no, 5, authorizer,
                                        end_time)

    def new_exam_member(self, user_no, exam_no, authorizer, **kwargs):
        items = self._select_exam_member(user_no, exam_no)
        now_time = time.time()
        if len(items) > 0:
            if items[0]['end_time'] > now_time:
                return 0
            return self.update_exam_member(user_no, exam_no, authorizer,
                                           **kwargs)
        return self._insert_exam_member(user_no, exam_no, 5, authorizer,
                                        **kwargs)

    def update_exam_member(self, user_no, exam_no, authorizer, **kwargs):
        end_time = kwargs.pop('end_time', None)
        if end_time is None:
            days = kwargs.pop('days', 0)
            if days > 0:
                end_time = time.time() + days * self.DAY_SECONDS
        return self._update_exam_member(user_no, exam_no, authorizer, end_time)

    def increase_exam_member(self, user_no, exam_no, authorizer, days):
        items = self._select_exam_member(user_no, exam_no)
        if items:
            end_time = items[0]['end_time']
            if end_time is not None:
                if end_time < time.time():
                    end_time = time.time()
                n_end_time = end_time + self.DAY_SECONDS * days
                self.update_exam_member(user_no, exam_no, authorizer,
                                        end_time=n_end_time)
        else:
            self.insert_exam_member(user_no, exam_no, authorizer, days=days)
        return self.user_exams(user_no, exam_no)[0]

    def insert_exam_owner(self, user_no, exam_no):
        return self._insert_exam_member(user_no, exam_no, 1, 0)


class ExamUsage(object):
    BASIC_PT = 1578240000  # 2020-01-06 00:00:00 Monday
    ONE_PERIOD = 7 * 24 * 60 * 60

    def __init__(self):
        self.t_usage = "exam_usage_records"
        self.cols_usage = ['period_no', 'exam_no', 'user_no', 'num',
                           'right_num', 'update_time']

    @classmethod
    def calc_period_no(cls, t=None):
        if not t:
            t = time.time()
        period_no = (t - cls.BASIC_PT) / cls.ONE_PERIOD
        return int(period_no)

    def get_usage_records(self, exam_no, user_no=None, period_no=None,
                          offset_num=1):
        if period_no is None:
            period_no = self.calc_period_no()
        where_value = dict(exam_no=exam_no)
        where_cond = []
        where_cond_args = []
        if offset_num > 1 and period_no != -1:  # period_no=-1 代表所有
            where_cond.append('period_no<=%s')
            where_cond_args.append(period_no)
            where_cond.append('period_no>=%s')
            where_cond_args.append(period_no - offset_num + 1)
        else:
            where_value['period_no'] = period_no
        if user_no:
            where_value['user_no'] = user_no
        items = self.db.execute_select(self.t_usage, cols=self.cols_usage,
                                       where_value=where_value,
                                       where_cond=where_cond,
                                       where_cond_args=where_cond_args)
        return items

    def get_usage_records_by_time(self, query_time, exam_no, user_no=None):
        period_no = self.calc_period_no(query_time)
        return self.get_usage_records(exam_no, user_no, period_no)

    def get_one_usage_records(self, user_no, exam_no, period_no=None):
        if period_no is None:
            period_no = self.calc_period_no()
        return self._get_one_usage_records(period_no, user_no, exam_no)

    def _get_one_usage_records(self, period_no, user_no, exam_no):
        items = self.get_usage_records(exam_no, user_no, period_no)
        if len(items) != 1:
            return {'num': 0, 'update_time': None, 'period_no': period_no,
                    'exam_no': exam_no, 'user_no': user_no, 'right_num': 0}
        return items[0]

    def get_one_ranking(self, exam_no, num, period_no=None):
        if period_no is None:
            period_no = self.calc_period_no()
        cols = ['count(*)']
        where_value = {'period_no': period_no, 'exam_no': exam_no}
        where_cond = ['num > %s']
        where_cond_args = [num]
        items = self.db.execute_select(
            self.t_usage, cols=cols, where_value=where_value,
            where_cond=where_cond, where_cond_args=where_cond_args)
        return list(items[0].values())[0]

    def update_usage_records(self, exam_no, user_no, num=1, right_num=0):
        if num <= 0:
            return None
        period_no = self.calc_period_no()
        return self._update_usage_records(period_no, exam_no, user_no, num,
                                          right_num)

    def _update_usage_records(self, period_no, exam_no, user_no, num=1,
                              right_num=0):
        if num <= 0:
            return None
        _num = num
        _right_num = right_num
        o_item = self._get_one_usage_records(period_no, user_no, exam_no)
        o_num = o_item['num']
        o_right_num = o_item['right_num']
        num += o_num
        right_num += o_right_num
        update_value = {'num': num, 'update_time': time.time(),
                        'right_num': right_num}
        where_value = dict(period_no=period_no, exam_no=exam_no,
                           user_no=user_no)
        if o_num == 0:
            update_value.update(where_value)
            self.db.execute_insert(self.t_usage, update_value)
        else:
            self.db.execute_update(self.t_usage, update_value=update_value,
                                   where_value=where_value)
            update_value.update(where_value)
        # period_no == -1 记录总的做题数
        if period_no != -1:
            self._update_usage_records(-1, exam_no, user_no, _num, _right_num)
        return update_value


class QuestionSources(object):

    def __init__(self, db):
        self.db = db
        self.cols = ['exam_no', 'question_source', 'update_time']
        self.t = 'exam_question_sources'

    def select_sources(self, exam_no):
        where_value = {'exam_no': exam_no}
        items = self.db.execute_select(self.t, cols=self.cols,
                                       where_value=where_value,
                                       order_by=['question_source'],
                                       order_desc=True)
        return items

    def insert_source(self, exam_no, question_source):
        if not question_source:
            return None
        u_time = time.time()
        data = {'exam_no': exam_no, 'question_source': question_source,
                'update_time': u_time}
        self.db.execute_duplicate_insert(self.t, kwargs=data,
                                         u_keys=['update_time'])
        return data


class ExamGenStrategy(BaseObject):
    model = exam_models.ExamGenStrategyModel

    def get_strategy(self, session, exam_no, strategy_id=None, internal=0):
        where_value = {'exam_no': exam_no}
        if strategy_id:
            where_value['strategy_id'] = strategy_id
        if internal is not None:
            where_value['internal'] = internal
        items = self.get_all(session, **where_value)
        d_items = []
        for _item in items:
            item = _item.to_dict()
            item['strategy_items'] = json.loads(item['strategy_items'])
            for si_item in item['strategy_items']:
                if 'qss' not in si_item:
                    si_item['qss'] = []
            d_items.append(item)
        return d_items

    def new_strategy(self, session, exam_no, strategy_items,
                        strategy_name='', internal=0):
        u_time = self.now_time
        strategy_id = uuid.uuid4().hex
        if strategy_items:
            strategy_items = json.dumps(strategy_items)
        data = {'exam_no': exam_no, 'strategy_id': strategy_id,
                'strategy_name': strategy_name,
                'strategy_items': strategy_items,
                'internal': internal,
                'update_time': u_time}
        self.create(session, **data)
        if data['strategy_items']:
            data['strategy_items'] = json.loads(data['strategy_items'])
        return data

    def update_strategy(self, session, exam_no, strategy_id,
                        strategy_name=None, strategy_items=None,
                        internal=None):
        u_time = self.now_time
        where_value = dict(strategy_id=strategy_id, exam_no=exam_no)
        data = {'update_time': u_time}
        if strategy_name:
            data['strategy_name'] = strategy_name
        if strategy_items:
            data['strategy_items'] = json.dumps(strategy_items)
        if internal is not None:
            data['internal'] = internal
        return self.update(session, where_value, **data)

    def delete_strategy(self, session, exam_no, strategy_id):
        where_value = dict(exam_no=exam_no, strategy_id=strategy_id)
        return self.delete(session, **where_value)


class Exam(ExamMember, ExamUsage):

    def __init__(self, db_conf_path):
        ExamMember.__init__(self)
        ExamUsage.__init__(self)
        self.db = DB(conf_path=db_conf_path)
        self.t_info = "exam_info"
        self.t_q = "exam_questions"
        self.t_w = "exam_wrong_answer"
        self.q_cols = ["exam_no", "question_no", "question_desc",
                       "question_desc_url", "select_mode", "options",
                       "answer", "question_subject", "question_source",
                       'question_source_no', "inside_mark", "answer_pic_url",
                       'question_chapter', 'state']
        self.qs_man = QuestionSources(self.db)
        self.qf_man = ExamQuestionFeedbackObj()
        self.strategy = ExamGenStrategy()

    def _insert_info(self, exam_no, exam_name, exam_desc, adder, status=1, exam_extend=None):
        kwargs = dict(exam_no=exam_no, exam_name=exam_name, exam_desc=exam_desc, status=status,
                      exam_extend=exam_extend, adder=adder)
        l = self.db.execute_insert(self.t_info, kwargs=kwargs, ignore=True)
        if l > 0:
            self.insert_exam_owner(adder, exam_no)
        return l

    def _insert_question(self, exam_no, question_no, question_desc,
                         select_mode, options, answer, **kwargs):
        data = dict(exam_no=exam_no, question_no=question_no,
                    question_desc=question_desc, select_mode=select_mode,
                    options=options, answer=answer)
        for key, value in kwargs.items():
            if key in self.q_cols:
                data[key] = value
        l = self.db.execute_insert(self.t_q, kwargs=data, ignore=True)
        if l and 'question_source' in kwargs:
            self.qs_man.insert_source(exam_no, kwargs['question_source'])
        return l

    def _insert_wrong_answer(self, user_no, exam_no, question_nos):
        cols = ["user_no", "exam_no", "question_no", "wrong_time", "wrong_freq"]
        wrong_time = int(time.time())
        values = list(map(lambda x: [user_no, exam_no, x, wrong_time, 1],
                          question_nos))
        l = self.db.execute_duplicate_insert_mul(self.t_w, cols, values, u_keys=["wrong_time"],
                                                 p1_keys=["wrong_freq"])
        return l

    def _update_info(self, exam_no, **update_value):
        where_value = dict(exam_no=exam_no)
        l = self.db.execute_update(self.t_info, update_value=update_value, where_value=where_value)
        return l

    def _update_status(self, exam_no, add_status=None, sub_status=None):
        where_value = dict(exam_no=exam_no)
        if add_status is not None:
            l = self.db.execute_update(self.t_info, update_value_list=["status=status|%s" % add_status],
                                       where_value=where_value)
        elif sub_status is not None:
            l = self.db.execute_update(self.t_info, update_value_list=["status=status&~%s" % sub_status],
                                       where_value=where_value)
        else:
            l = 0
        return l

    def _update_num(self, exam_no):
        where_value = dict(exam_no=exam_no)
        l = self.db.execute_update(self.t_info, update_value_list=["exam_num=exam_num+1"], where_value=where_value)
        return l

    def _update_question(self, exam_no, question_no, **kwargs):
        where_value = dict(exam_no=exam_no, question_no=question_no)
        l = self.db.execute_update(self.t_q, update_value=kwargs,
                                   where_value=where_value)
        if l and 'question_source' in kwargs:
            self.qs_man.insert_source(exam_no, kwargs['question_source'])
        return l

    def new_exam(self, exam_name, exam_desc, adder, **exam_extend):
        exam_no = int(time.time())
        l = self._insert_info(exam_no, exam_name, exam_desc, adder, exam_extend=exam_extend)
        if l <= 0:
            return False, l
        return True, exam_no

    def new_exam_questions(self, exam_no, question_no, question_desc, select_mode, options, answer, **kwargs):
        l = self._insert_question(exam_no, question_no, question_desc, select_mode, options, answer, **kwargs)
        if l <= 0:
            return False, l
        self._update_info(exam_no, question_num=question_no)
        self._update_status(exam_no, add_status=2)
        return True, l

    def new_exam_wrong(self, user_no, exam_no, question_no):
        if isinstance(question_no, list):
            question_nos = question_no
        elif isinstance(question_no, int):
            question_nos = [question_no]
        else:
            question_nos = filter(lambda x: len(x) > 0, re.split("\D", question_no))
        if len(question_nos) <= 0:
            return 0
        return self._insert_wrong_answer(user_no, exam_no, question_nos)

    def update_exam(self, exam_no, exam_name, exam_desc, **exam_extend):
        update_value = dict(exam_name=exam_name, exam_desc=exam_desc, exam_extend=exam_extend)
        l = self._update_info(exam_no, **update_value)
        return l

    def update_exam_questions(self, exam_no, question_no, question_desc=None, select_mode=None,
                              options=None, answer=None, question_desc_url=None, **update_data):
        kwargs = dict()
        if question_desc is not None:
            kwargs["question_desc"] = question_desc
        if select_mode is not None:
            kwargs["select_mode"] = select_mode
        if options is not None:
            kwargs["options"] = options
            for item in options:
                for key in item.keys():
                    if key not in ("score", "desc"):
                        del item[key]
        if answer is not None:
            kwargs["answer"] = answer

        if question_desc_url is not None:
            kwargs["question_desc_url"] = question_desc_url
            if len(question_desc_url) == 0:
                kwargs["question_desc_url"] = None
        for key, value in update_data.items():
            if key in self.q_cols:
                kwargs[key] = value
        l = self._update_question(exam_no, question_no, **kwargs)
        return l

    def select_exam(self, exam_no, offline, user_no=None):
        where_value = dict()
        where_cond = ["status<>0"]
        if exam_no is not None:
            where_value["exam_no"] = exam_no
        cols = ["exam_no", "exam_name", "exam_desc", "adder", "status",
                "exam_extend", "exam_num", "question_num"]
        items = self.db.execute_select(self.t_info, cols=cols,
                                       where_value=where_value,
                                       where_cond=where_cond)
        for item in items:
            if item["exam_extend"] is not None:
                item['exam_extend'] = json.loads(item["exam_extend"])
                item.update(item['exam_extend'])
        if not offline:
            items = [item for item in items
                     if item['status'] & constants.STATUS_OFFLINE == 0
                     or user_no == int(item['adder'])]
        return items

    def select_exam2(self, exam_no, offline=False, user_no=None):
        items = self.select_exam(exam_no, offline=offline, user_no=user_no)
        return [ExamObject(**item) for item in items]

    def get_exam_role(self, exam_no, user_no):
        exist_items = self.select_exam2(exam_no, offline=True)
        if len(exist_items) <= 0:
            return None
        if int(exist_items[0].adder) == user_no:
            exam_role = 1
        else:
            e_items = self.user_exams(user_no, exam_no)
            if len(e_items) <= 0:
                exam_role = exist_items[0].exam_role
            else:
                exam_role = e_items[0]['exam_role']
        return exam_role

    def _select_questions(self, **kwargs):
        cols = self.q_cols
        items = self.db.execute_select(self.t_q, cols=cols, **kwargs)
        for item in items:
            item["options"] = json.loads(item["options"])
            if item['select_mode'] in constants.G_MULTI_MODE:
                item['multi'] = True  # 答案多选
            else:
                item['multi'] = False
        return items

    def select_one_question(self, exam_no, question_no):
        where_value = {'exam_no': exam_no, 'question_no': question_no}
        items = self._select_questions(where_value=where_value)
        if len(items) <= 0:
            return None
        return items[0]

    def select_questions(self, exam_no, start_no=None, num=None, desc=False):
        where_value = dict(exam_no=exam_no)
        where_cond = []
        where_cond_args = []
        if start_no is not None:
            if desc is False:
                where_cond.append("question_no>=%s")
            else:
                where_cond.append("question_no<=%s")

            where_cond_args.append(start_no)
        limit = num
        items = self._select_questions(where_value=where_value, where_cond=where_cond,
                                       where_cond_args=where_cond_args, limit=limit,
                                       order_by=["question_no"],
                                       order_desc=desc)
        if desc is True:
            items.reverse()
        return items

    def select_max_question(self, exam_no):
        cols = ["max(question_no)"]
        items = self.db.execute_select(self.t_q, where_value=dict(exam_no=exam_no), cols=cols)
        if len(items) <= 0:
            return 0
        max_no = items[0]["max(question_no)"]
        if max_no is None:
            return 0
        return max_no

    def select_question_no(self, exam_no, select_mode=None, start_no=None,
                           question_subject=None, question_chapter=None,
                           question_source=None):
        where_value = dict(exam_no=exam_no, state=0)
        order_by = None
        if select_mode is not None and select_mode >= 0:
            where_value['select_mode'] = select_mode
        if question_subject is not None:
            where_value['question_subject'] = question_subject
        if question_chapter is not None:
            where_value['question_chapter'] = question_chapter
        if question_source is not None:
            where_value['question_source'] = question_source
            order_by = ['question_source_no']
        where_cond_args = []
        where_cond = []
        if start_no is not None:
            where_cond.append('question_no>=%s')
            where_cond_args.append(start_no)
        cols = self.q_cols[:2]

        items = self.db.execute_select(self.t_q, cols=cols,
                                       where_value=where_value,
                                       where_cond=where_cond,
                                       where_cond_args=where_cond_args,
                                       order_by=order_by)
        return items

    def select_random_questions(self, exam_no, num, select_mode=None,
                                question_subject=None, exclude_nos=""):
        """
        :param exam_no:
        :param num: 如果num小于0获取全部
        :param select_mode:
        :param question_subject:
        :param exclude_nos:
        :return:
        """
        m_items = self.select_question_no(exam_no, select_mode, None,
                                          question_subject)
        exclude_set = set([int(x) for x in re.split('\D', exclude_nos)
                           if x != ''])
        m_nos = set(map(lambda x: x["question_no"], m_items)) - exclude_set
        m_nos_len = len(m_nos)
        if m_nos_len <= 0:
            return []
        if num > m_nos_len or num < 0:
            return self.select_multi_question(exam_no, m_nos)
        q_nos = random.sample(m_nos, num)
        return self.select_multi_question(exam_no, q_nos)

    def get_questions_by_strategy(self, exam_no, strategy_id,
                                  question_subject=None):
        strategies = self.get_strategy(exam_no, strategy_id)
        if len(strategies) <= 0:
            return []
        strategy_items = strategies[0]['strategy_items']
        questions = []
        for item in strategy_items:
            _qts = self.select_random_questions(exam_no, item['num'],
                                                item['value'],
                                                question_subject)
            questions.extend(_qts)
        return questions

    def get_questions_by_strategy_items(self, exam_no, strategy_items):
        questions = []
        for item in strategy_items:
            question_subjects = item.get('question_subjects', [None])
            for qs in question_subjects:
                _qts = self.select_random_questions(exam_no, item['num'],
                                                    item['value'], qs)
                questions.extend(_qts)
        return questions

    def select_multi_question(self, exam_no, q_nos):
        if len(q_nos) <= 0:
            return []
        cols = self.q_cols
        sql_f = "SELECT %s FROM %s WHERE exam_no=%s AND question_no={0}" % (",".join(cols), self.t_q, exam_no)
        sql = " UNION ".join(map(lambda x: sql_f.format(x), q_nos))
        self.db.execute(sql)
        items = self.db.fetchall()
        d_items = []
        for item in items:
            d_item = dict()
            for i in range(len(cols)):
                d_item[cols[i]] = item[i]
            d_item["options"] = json.loads(d_item["options"])
            d_items.append(d_item)
        return d_items

    def select_multi_question2(self, exam_no, q_nos):
        if len(q_nos) <= 0:
            return []
        else:
            q_nos = [str(no) for no in q_nos]
        cols = self.q_cols
        sql_f = "SELECT %s FROM %s WHERE exam_no=%s AND question_no in (%s);" \
                % (",".join(cols), self.t_q, exam_no, ','.join(q_nos))
        self.db.execute(sql_f)
        items = self.db.fetchall()
        d_items = []
        for item in items:
            d_item = dict()
            for i in range(len(cols)):
                d_item[cols[i]] = item[i]
            d_item["options"] = json.loads(d_item["options"])
            if d_item['select_mode'] in constants.G_MULTI_MODE:
                d_item['multi'] = True  # 答案多选
            else:
                d_item['multi'] = False
            d_items.append(d_item)
        return d_items

    def select_wrong(self, user_no, exam_no, min_wrong_time=0):
        where_value = dict(user_no=user_no, exam_no=exam_no)
        where_cond = ["wrong_time>%s"]
        where_cond_args = (min_wrong_time, )
        cols = ["user_no", "exam_no", "question_no", "wrong_time", "wrong_freq"]
        items = self.db.execute_select(self.t_w, where_value=where_value, cols=cols, where_cond=where_cond,
                                       where_cond_args=where_cond_args)
        return items

    def online_exam(self, exam_no):
        self._update_status(exam_no, sub_status=constants.STATUS_OFFLINE)
        l = self._update_status(exam_no, add_status=64)
        return l

    def offline_exam(self, exam_no):
        self._update_status(exam_no, sub_status=64)
        l = self._update_status(exam_no, add_status=constants.STATUS_OFFLINE)
        return l

    def delete_exam(self, exam_no):
        l = self._update_info(exam_no, status=0)
        return l

    def delete_wrong(self, user_no, exam_no, question_no):
        where_value = dict(user_no=user_no, exam_no=exam_no, question_no=question_no)
        l = self.db.execute_delete(self.t_w, where_value=where_value)
        return l

    def transfer_exam(self, source_exam_no, source_start_no, source_end_no,
                      target_exam_no, **kwargs):
        where_value = dict(exam_no=source_exam_no)
        if 'select_mode' in kwargs:
            select_mode = kwargs.pop('select_mode')
            if isinstance(select_mode, int):
                where_value['select_mode'] = select_mode
        where_cond = ['question_no>=%s', 'question_no<=%s']
        where_cond_args = [source_start_no, source_end_no]
        items = self._select_questions(where_value=where_value,
                                       where_cond=where_cond,
                                       where_cond_args=where_cond_args)
        if kwargs.pop('random', False):
            random.shuffle(items)
        if 'target_start_no' in kwargs:
            t_start_no = kwargs['target_start_no']
            if 'target_end_no' not in kwargs:
                t_end_no = t_start_no + len(items) - 1
            else:
                t_end_no = kwargs['target_end_no']
                if t_end_no - t_start_no != len(items) - 1:
                    return False, 'Not match questions length'
            for index in range(len(items)):
                item = items[index]
                item['question_no'] = t_start_no + index
                item['exam_no'] = target_exam_no
                self.update_exam_questions(**item)
        else:
            next_no = self.select_max_question(target_exam_no) + 1
            for item in items:
                item['question_no'] = next_no
                item['exam_no'] = target_exam_no
                self.new_exam_questions(**item)
                next_no += 1
        return True, items

    def get_sources(self, exam_no):
        return self.qs_man.select_sources(exam_no)

    def query_questions(self, exam_no, query_str):
        query_str = query_str.strip()
        if len(query_str) <= 3:
            return []
        where_value = dict(exam_no=exam_no)
        where_cond = ["question_desc LIKE %s"]
        where_cond_args = [u'%{0}%'.format(query_str)]
        items = self._select_questions(where_value=where_value,
                                       where_cond=where_cond,
                                       where_cond_args=where_cond_args,
                                       limit=10)
        return items

    def user_exam_role(self, sys_user_role, user_no, exam_no):
        exist_items = self.select_exam2(exam_no)
        if len(exist_items) <= 0:
            return None, None
        exam_item = exist_items[0]
        if(sys_user_role & 2) == 2:
            exam_role = 0
        else:
            if int(exam_item.adder) == user_no:
                exam_role = 1
            else:
                e_items = self.user_exams(user_no, exam_no)
                if len(e_items) <= 0:
                    exam_role = exam_item.exam_role
                else:
                    exam_role = e_items[0]['exam_role']
        return exam_item, exam_role


class ExamInfo(BaseObject):
    model = exam_models.ExamInfoModel

    def get_online(self, session, exam_no=None):
        kwargs = {}
        if exam_no:
            kwargs['exam_no'] = exam_no
        items = self.get_all(session, **kwargs)
        n_items = [item for item in items
                   if item.status & constants.STATUS_ONLINE != 0]
        return n_items

    def get_private(self, session, exam_no=None):
        items = self.get_online(session, exam_no=exam_no)
        items = [item for item in items if item.is_private()]
        return items


class ExamMemberFlow2(BaseObject):
    model = exam_models.ExamMemberFlowModel

    def get_flows(self, session, user_no, exam_no):
        return self.get_all(session, user_no=user_no, exam_no=exam_no)


if __name__ == "__main__":
    # print(ExamUsage.calc_period_no(1578844800))
    e = Exam("../mysql_app.conf")
    e._insert_exam_member(3, 1551600675, 2, 1)
    # e.select_max_question("1543289889")

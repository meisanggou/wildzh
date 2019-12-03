# !/usr/bin/env python
# coding: utf-8

import re
import time
import json
import random
import string
from mysqldb_rich.db2 import DB

__author__ = 'meisa'

"""
题库角色exam_role
0 内部用户
1 拥有者： 所有权限
2 超级管理员：可更新题库信息 授权新的管理员
3 管理员：新增试题，更新试题 授权普通用户
5 普通成员： 可做题


10 公开题库 可做题
"""


class ExamMember(object):

    def __init__(self):
        self.t_em = "exam_member"

    def user_exams(self, user_no, exam_no=None):
        where_value = dict(user_no=user_no)
        if exam_no:
            where_value['exam_no'] = exam_no
        cols = ['user_no', 'exam_no', 'exam_role']
        items = self.db.execute_select(self.t_em, cols=cols,
                                       where_value=where_value)
        return items

    def select_user_exams(self, user_no):
        items = self.user_exams(user_no)
        e_dict = dict()
        for item in items:
            e_dict[item['exam_no']] = item
        return e_dict

    def insert_exam_member(self, user_no, exam_no, authorizer):
        return self._insert_exam_member(user_no, exam_no, 5, authorizer)

    def _insert_exam_member(self, user_no, exam_no, exam_role, authorizer):
        data = dict(user_no=user_no, exam_no=exam_no, exam_role=exam_role,
                    authorizer=authorizer)
        data['insert_time'] = time.time()
        data['update_time'] = time.time()
        l = self.db.execute_insert(self.t_em, data)
        return l

    def insert_exam_owner(self, user_no, exam_no):
        return self._insert_exam_member(user_no, exam_no, 1, 0)


class Exam(ExamMember):

    def __init__(self, db_conf_path):
        super(Exam, self).__init__()
        self.db = DB(conf_path=db_conf_path)
        self.t_info = "exam_info"
        self.t_q = "exam_questions"
        self.t_w = "exam_wrong_answer"
        self.q_cols = ["exam_no", "question_no", "question_desc",
                       "question_desc_url", "select_mode", "options",
                       "answer", "question_subject", "question_source",
                       "inside_mark", "answer_pic_url"]

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
        return l

    def _insert_wrong_answer(self, user_no, exam_no, question_nos):
        cols = ["user_no", "exam_no", "question_no", "wrong_time", "wrong_freq"]
        wrong_time = int(time.time())
        values = map(lambda x: [user_no, exam_no, x, wrong_time, 1], question_nos)
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
        l = self.db.execute_update(self.t_q, update_value=kwargs, where_value=where_value)
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

    def select_exam(self, exam_no):
        where_value = dict()
        where_cond = ["status<>0"]
        if exam_no is not None:
            where_value["exam_no"] = exam_no
        cols = ["exam_no", "exam_name", "exam_desc", "adder", "status",
                "exam_extend", "exam_num", "question_num"]
        items = self.db.execute_select(self.t_info, cols=cols, where_value=where_value, where_cond=where_cond)
        for item in items:
            item["exam_type"] = "tiku"
            if item["exam_extend"] is not None:
                item.update(json.loads(item["exam_extend"]))
                del item["exam_extend"]
        return items

    def _select_questions(self, **kwargs):
        cols = self.q_cols
        items = self.db.execute_select(self.t_q, cols=cols, **kwargs)
        for item in items:
            item["options"] = json.loads(item["options"])
        return items

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
        for item in items:
            item["options"] = json.loads(item["options"])
        if desc is True:
            items.reverse()
        return items

    def select_max_question(self, exam_no):
        cols = ["max(question_no)"]
        items = self.db.execute_select(self.t_q, where_value=dict(exam_no=exam_no), cols=cols)
        if len(items) <= 0:
            return 0
        return items[0]["max(question_no)"]

    def select_question_no(self, exam_no, select_mode=None, question_subject=None):
        where_value = dict(exam_no=exam_no)
        if select_mode is not None:
            where_value['select_mode'] = select_mode
        if question_subject is not None:
            where_value['question_subject'] = question_subject
        cols = self.q_cols[:2]
        items = self.db.execute_select(self.t_q, cols=cols, where_value=where_value)
        return items

    def select_random_questions(self, exam_no, num, select_mode=None, question_subject=None):
        m_items = self.select_question_no(exam_no, select_mode, question_subject)
        m_nos = map(lambda x: x["question_no"], m_items)
        m_nos_len = len(m_nos)
        if m_nos_len <= 0:
            return []
        if num > m_nos_len:
            return self.select_multi_question(exam_no, m_nos)
        q_nos = random.sample(m_nos, num)
        return self.select_multi_question(exam_no, q_nos)

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

    def select_wrong(self, user_no, exam_no, min_wrong_time=0):
        where_value = dict(user_no=user_no, exam_no=exam_no)
        where_cond = ["wrong_time>%s"]
        where_cond_args = (min_wrong_time, )
        cols = ["user_no", "exam_no", "question_no", "wrong_time", "wrong_freq"]
        items = self.db.execute_select(self.t_w, where_value=where_value, cols=cols, where_cond=where_cond,
                                       where_cond_args=where_cond_args)
        return items

    def online_exam(self, exam_no):
        l = self._update_status(exam_no, add_status=64)
        return l

    def offline_exam(self, exam_no):
        l = self._update_status(exam_no, sub_status=64)
        return l

    def delete_exam(self, exam_type, exam_no):
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
            where_value['select_mode'] = kwargs.pop('select_mode')
        where_cond = ['question_no>=%s', 'question_no<=%s']
        where_cond_args = [source_start_no, source_end_no]
        items = self._select_questions(where_value=where_value,
                                       where_cond=where_cond,
                                       where_cond_args=where_cond_args)
        next_no = self.select_max_question(target_exam_no) + 1
        for item in items:
            item['question_no'] = next_no
            item['exam_no'] = target_exam_no
            self.new_exam_questions(**item)
            next_no += 1
        return items

if __name__ == "__main__":
    e = Exam("../mysql_app.conf")
    e.select_max_question("1543289889")

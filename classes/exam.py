# !/usr/bin/env python
# coding: utf-8

import time
import json
from mysqldb_rich import DB

__author__ = 'meisa'


class Exam(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t_info = "exam_info"
        self.t_result_explain = "exam_result_explain"
        self.t_tj = "exam_tj"
        self.t_records = "exam_records"
        self.t_q = "exam_questions"
        pass

    def _insert_info(self, exam_type, exam_no, exam_name, exam_desc, eval_type, adder, status=1, exam_extend=None):
        kwargs = dict(exam_type=exam_type, exam_no=exam_no, exam_name=exam_name, exam_desc=exam_desc,
                      eval_type=eval_type, status=status, exam_extend=exam_extend, adder=adder)
        l = self.db.execute_insert(self.t_info, kwargs=kwargs, ignore=True)
        return l

    def _insert_result_explain(self, exam_no, case_a, case_b, case_c=None, case_d=None, case_e=None, case_f=None):
        kwargs = dict(exam_no=exam_no, case_a=case_a, case_b=case_b, case_c=case_c, case_d=case_d, case_e=case_e,
                      case_f=case_f)
        l = self.db.execute_insert(self.t_result_explain, kwargs=kwargs, ignore=True)
        return l

    def _insert_tj(self, exam_no):
        kwargs = dict(exam_no=exam_no)
        l = self.db.execute_insert(self.t_tj, kwargs=kwargs, ignore=True)
        return l

    def _insert_records(self, exam_no, result, times=0, user_id=None):
        kwargs = dict(exam_no=exam_no, result=result, times=times, user_id=user_id)
        l = self.db.execute_insert(self.t_records, kwargs=kwargs, ignore=True)
        return l

    def _insert_question(self, exam_no, question_no, question_desc, select_mode, options):
        kwargs = dict(exam_no=exam_no, question_no=question_no, question_desc=question_desc, select_mode=select_mode,
                      options=options)
        l = self.db.execute_insert(self.t_q, kwargs=kwargs, ignore=True)
        return l

    def _update_info(self, exam_type, exam_no, **update_value):
        where_value = dict(exam_no=exam_no, exam_type=exam_type)
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

    def new_exam(self, exam_name, exam_type, exam_desc, eval_type, adder, **exam_extend):
        exam_no = int(time.time())
        l = self._insert_info(exam_type, exam_no, exam_name, exam_desc, eval_type, adder, exam_extend=exam_extend)
        if l <= 0:
            return False, l
        return True, exam_no

    def new_exam_result_explain(self, exam_no, case_a, case_b, case_c=None, case_d=None, case_e=None, case_f=None):
        l = self._insert_result_explain(exam_no, case_a, case_b, case_c, case_d, case_e, case_f)
        l2 = self._update_status(exam_no, add_status=4)
        return min(l, l2)

    def new_exam_questions(self, exam_no, question_no, question_desc, select_mode, options):
        l = self._insert_question(exam_no, question_no, question_desc, select_mode, options)
        if l <= 0:
            return False, l
        self._update_status(exam_no, add_status=2)
        return True, l

    def update_exam_questions(self, exam_no, question_no, question_desc=None, select_mode=None, options=None):
        kwargs = dict()
        if question_desc is not None:
            kwargs["question_desc"] = question_desc
        if select_mode is not None:
            kwargs["select_mode"] = select_mode
        if options is not None:
            kwargs["options"] = options
        l = self._update_question(exam_no, question_no, **kwargs)
        return l

    def select_exam(self, exam_type, exam_no=None):
        where_value = dict()
        where_cond = ["status<>0"]
        if exam_type is not None:
            where_value = dict(exam_type=exam_type)
            if exam_no is not None:
                where_value["exam_no"] = exam_no
        cols = ["exam_type", "exam_no", "exam_name", "exam_desc", "eval_type", "adder", "status",
                "exam_extend", "exam_num"]
        items = self.db.execute_select(self.t_info, cols=cols, where_value=where_value, where_cond=where_cond)
        return items

    def select_questions(self, exam_no):
        where_value = dict(exam_no=exam_no)
        cols = ["exam_no", "question_no", "question_desc", "select_mode", "options"]
        items = self.db.execute_select(self.t_q, cols=cols, where_value=where_value)
        for item in items:
            item["options"] = json.loads(item["options"])
        return items

    def online_exam(self, exam_no):
        l = self._update_status(exam_no, add_status=8)
        return l

    def delete_exam(self, exam_type, exam_no):
        l = self._update_info(exam_type, exam_no, status=0)
        return l

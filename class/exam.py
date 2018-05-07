# !/usr/bin/env python
# coding: utf-8

from JYTools.DB import DB

__author__ = 'meisa'


class Exam(object):

    def __init__(self):
        self.db = DB()
        self.t_info = "exam_info"
        self.t_result_explain = "exam_result_explain"
        self.t_tj = "exam_tj"
        self.t_records = "exam_records"
        self.t_q = "exam_questions"
        pass

    def _insert_info(self, exam_type, exam_no, exam_name, exam_desc, eval_type, status=0, exam_extend=None):
        kwargs = dict(exam_type=exam_type, exam_no=exam_no, exam_name=exam_name, exam_desc=exam_desc,
                      eval_type=eval_type, status=status, exam_extend=exam_extend)
        l = self.db.execute_insert(self.t_info, kwargs=kwargs, ignore=True)
        return l

    def _insert_result_explain(self, exam_no, case_a, case_b=None, case_c=None, case_d=None, case_e=None, case_f=None):
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

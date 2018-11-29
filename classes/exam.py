# !/usr/bin/env python
# coding: utf-8

import re
import time
import json
import random
import string
from mysqldb_rich.db2 import DB

__author__ = 'meisa'


class Exam(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t_info = "exam_info"
        self.t_result_explain = "exam_result_explain"
        self.t_tj = "exam_tj"
        self.t_records = "exam_records"
        self.t_q = "exam_questions"
        self.t_w = "exam_wrong_answer"

    def _insert_info(self, exam_no, exam_name, exam_desc, eval_type, adder, status=1, exam_extend=None):
        kwargs = dict(exam_no=exam_no, exam_name=exam_name, exam_desc=exam_desc, eval_type=eval_type, status=status,
                      exam_extend=exam_extend, adder=adder)
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

    def _add_tj(self, exam_no, *amount_case):
        update_value_list = []
        for key in amount_case:
            update_value_list.append("{key}={key}+1".format(key=key))
        where_value = dict(exam_no=exam_no)
        l = self.db.execute_update(self.t_tj, update_value_list=update_value_list, where_value=where_value)
        return l

    def _insert_records(self, user_id, exam_no, result):
        insert_time = int(time.time())
        kwargs = dict(exam_no=exam_no, result=result, insert_time=insert_time, user_id=user_id)
        l = self.db.execute_insert(self.t_records, kwargs=kwargs, ignore=True)
        return l

    def _insert_question(self, exam_no, question_no, question_desc, select_mode, options, answer):
        kwargs = dict(exam_no=exam_no, question_no=question_no, question_desc=question_desc, select_mode=select_mode,
                      options=options, answer=answer)
        l = self.db.execute_insert(self.t_q, kwargs=kwargs, ignore=True)
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

    def new_exam(self, exam_name, exam_type, exam_desc, eval_type, adder, **exam_extend):
        exam_no = int(time.time())
        l = self._insert_info(exam_no, exam_name, exam_desc, eval_type, adder, exam_extend=exam_extend)
        if l <= 0:
            return False, l
        return True, exam_no

    def new_exam_result_explain(self, exam_no, case_a, case_b, case_c=None, case_d=None, case_e=None, case_f=None):
        l = self._insert_result_explain(exam_no, case_a, case_b, case_c, case_d, case_e, case_f)
        l2 = self._update_status(exam_no, add_status=4)
        return min(l, l2)

    def new_exam_questions(self, exam_no, question_no, question_desc, select_mode, options, answer):
        l = self._insert_question(exam_no, question_no, question_desc, select_mode, options, answer)
        if l <= 0:
            return False, l
        self._update_info(exam_no, question_num=question_no)
        self._update_status(exam_no, add_status=2)
        return True, l

    def new_exam_record(self, user_id, exam_no, result):
        if len(result) != 1 or result not in string.letters[:6]:
            return False, result
        self._insert_records(user_id, exam_no, result)
        self._add_tj(exam_no, "amount_%s" % result)
        self._update_num(exam_no)
        return True, None

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

    def update_exam(self, exam_no, exam_name, exam_desc, eval_type, **exam_extend):
        update_value = dict(exam_name=exam_name, exam_desc=exam_desc, eval_type=eval_type, exam_extend=exam_extend)
        l = self._update_info(exam_no, **update_value)
        return l

    def update_result_explain(self, exam_no, case_a, case_b, case_c=None, case_d=None, case_e=None, case_f=None):
        kwargs = dict(case_a=case_a, case_b=case_b, case_c=case_c, case_d=case_d, case_e=case_e, case_f=case_f)
        l = self.db.execute_update(self.t_result_explain, update_value=kwargs, where_value=dict(exam_no=exam_no))
        return l

    def update_exam_questions(self, exam_no, question_no, question_desc=None, select_mode=None, options=None,
                              answer=None):
        kwargs = dict()
        if question_desc is not None:
            kwargs["question_desc"] = question_desc
        if select_mode is not None:
            kwargs["select_mode"] = select_mode
        if options is not None:
            kwargs["options"] = options
        if answer is not None:
            kwargs["answer"] = answer
        l = self._update_question(exam_no, question_no, **kwargs)
        return l

    def select_exam(self, exam_no):
        where_value = dict()
        where_cond = ["status<>0"]
        if exam_no is not None:
            where_value["exam_no"] = exam_no
        cols = ["exam_no", "exam_name", "exam_desc", "eval_type", "adder", "status",
                "exam_extend", "exam_num", "question_num"]
        items = self.db.execute_select(self.t_info, cols=cols, where_value=where_value, where_cond=where_cond)
        for item in items:
            item["exam_type"] = "tiku"
            if item["exam_extend"] is not None:
                item.update(json.loads(item["exam_extend"]))
                del item["exam_extend"]
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
        cols = ["exam_no", "question_no", "question_desc", "select_mode", "options", "answer"]
        items = self.db.execute_select(self.t_q, cols=cols, where_value=where_value, where_cond=where_cond,
                                       where_cond_args=where_cond_args, limit=limit, order_by=["question_no"],
                                       order_desc=desc, print_sql=True)
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

    def select_random_questions(self, exam_no, num):
        exam_items = self.select_exam(exam_no)
        if len(exam_items) <= 0:
            return []
        question_num = exam_items[0]["question_num"]
        if num > question_num:
            num = question_num
        q_nos = random.sample(range(1, question_num + 1), num)
        if len(q_nos) <= 0:
            return []
        cols = ["exam_no", "question_no", "question_desc", "select_mode", "options", "answer"]
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

    def select_result_explain(self, exam_no, result=None):
        cols = ["exam_no"]
        if result is None:
            for c in string.letters[:6]:
                cols.append("case_%s" % c)
        else:
            cols.append("case_%s" % result)
        items = self.db.execute_select(self.t_result_explain, cols=cols, where_value=dict(exam_no=exam_no))
        for item in items:
            for key, v in item.items():
                if key.startswith("case_") is False:
                    continue
                if v is None:
                    continue
                item[key] = json.loads(item[key])
        return items

    def select_tj(self, exam_no, merge_v=True):
        cols = ["exam_no"]
        for c in string.letters[:6]:
            cols.append("amount_%s" % c)
            cols.append("amount_v%s" % c)
        items = self.db.execute_select(self.t_tj, cols=cols, where_value=dict(exam_no=exam_no))
        if merge_v is False:
            return items
        for item in items:
            for c in string.letters[:6]:
                o_key = "amount_%s" % c
                v_key = "amount_v%s" % c
                item[o_key] += item[v_key]
                del item[v_key]
        return items

    def online_exam(self, exam_no):
        l = self._update_status(exam_no, add_status=64)
        l2 = self._insert_tj(exam_no)
        return min(l, l2)

    def delete_exam(self, exam_type, exam_no):
        l = self._update_info(exam_no, status=0)
        return l

if __name__ == "__main__":
    e = Exam("../mysql_app.conf")
    e.select_max_question("1543289889")
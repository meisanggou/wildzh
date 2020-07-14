# !/usr/bin/env python
# coding: utf-8
import json
import sys

from mysqldb_rich.db2 import DB
from zh_config import db_conf_path

__author__ = 'zhouhenglc'


def set_question_source_no():
    cols = ['exam_no', 'question_no', 'question_source', 'inside_mark']
    t = 'exam_questions'
    db = DB(db_conf_path)
    where_cond = ['question_source is not null']
    items = db.execute_select(t, cols=cols, where_cond=where_cond)
    for item in items:
        qs = item['question_source']
        if not item['inside_mark'].startswith(qs):
            sys.stderr.write(json.dumps(item))
            exit(1)
        question_source_no = int(item['inside_mark'].rsplit(' ', 1)[1])
        where_value = dict(exam_no=item['exam_no'], question_no=item['question_no'])
        update_value = dict(question_source_no=question_source_no)
        db.execute_update(t, update_value=update_value, where_value=where_value)


if __name__ == '__main__':
    set_question_source_no()

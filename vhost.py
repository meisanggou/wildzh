# !/usr/bin/env python
# coding: utf-8

from mysqldb_rich.db2 import DB


db = DB(conf_path="mysql_app.conf")

t = "exam_wrong_answer"
cols = ["user_no", "exam_no", "question_no", "wrong_freq", "wrong_time"]
items = db.execute_select(t, cols=cols, where_value=dict(exam_no=1543459550))
question_no = 0
exam_no = 1569283516

for item in items:
    item.update(question_no=question_no + item["question_no"], exam_no=exam_no)
    db.execute_insert(t, item)

question_no = 3416
items = db.execute_select(t, cols=cols, where_value=dict(exam_no=1543459598))
for item in items:
    item.update(question_no=question_no + item["question_no"], exam_no=exam_no)
    db.execute_insert(t, item)


question_no = 3954
items = db.execute_select(t, cols=cols, where_value=dict(exam_no=1543459703))
for item in items:
    item.update(question_no=question_no + item["question_no"], exam_no=exam_no)
    db.execute_insert(t, item)


question_no = 4294
items = db.execute_select(t, cols=cols, where_value=dict(exam_no=1543459998))
for item in items:
    item.update(question_no=question_no + item["question_no"], exam_no=exam_no)
    db.execute_insert(t, item)


question_no = 4392
items = db.execute_select(t, cols=cols, where_value=dict(exam_no=1543460024))
for item in items:
    item.update(question_no=question_no + item["question_no"], exam_no=exam_no)
    db.execute_insert(t, item)
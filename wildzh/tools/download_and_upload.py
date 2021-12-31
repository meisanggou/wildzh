# !/usr/bin/env python
# coding: utf-8
import json
import os
import re
import requests

from wildzh.tools.handle_exam import login
from wildzh.tools.handle_exam import post_questions
from wildzh.tools.handle_exam import upload_media_to_server
from wildzh.tools.parse_option import ListOption
from wildzh.tools.parse_option import Option
from wildzh.tools.parse_question import Question
from wildzh.tools.parse_question import QuestionSet
from wildzh.tools.parse_question import QuestionType

__author__ = 'zhouhenglc'


def load_file(name):
    with open(name, 'r') as r:
        c = r.read()
        data = json.loads(c)
        return data


OPTION_C = ['A', 'B', 'C', 'D', 'E', 'F']

# 单选64
# 判断16
OPTION_TYPE_MAP = {0: [QuestionType.Judge, 7],   # question_type select_mode
                   1: [QuestionType.Choice, 1],  # 选择
                   2: [QuestionType.Choice, 6]}  # 多选


def convert_to_question(data):
    answer = data['answer']
    option_type = data['optionType']

    lo = ListOption()
    as_basic = 16 # OPTION_TYPE_MAP[option_type][1]
    for c in OPTION_C:
        _dc = 'option%s' % c
        if _dc in data and data[_dc] is not None and data[_dc].strip():
            setattr(lo, c, data[_dc])
            getattr(lo, c).score = 1 if as_basic & answer else 0
            as_basic = int(as_basic * 2)
        else:
            break
    o_no = data['questionId']
    q = Question()
    q.no = o_no
    q.desc = data['question']
    q.options = lo
    if option_type not in OPTION_TYPE_MAP:
        print(data)
    q.q_type = OPTION_TYPE_MAP[option_type][0]
    q.select_mode = OPTION_TYPE_MAP[option_type][1]
    q.answer = data['conciseExplain']

    if data['mediaKey']:
        name = data['mediaContent'].rsplit('/', 1)[-1]
        _path = 'pics/%s.%s' % (o_no, name)
        q.desc_url = _path
    q.inside_mark = '%s' % (o_no, )
    return q


def list_files_and_upload(server):
    _o_cwd = os.getcwd()
    q_dir = 'D:/Project/daily/驾考宝典/questions4'
    files = os.listdir(q_dir)
    os.chdir(q_dir)
    QS = QuestionSet(exam_no='1640171496', dry_run=True,
                     question_subject=1, exam_name='驾考宝典-科目四')  # 0 科目一 1科目四
    for file in files:
        if file.startswith('.'):
            continue
        if os.path.isfile(file):
            j_data = load_file(file)
            q_obj = convert_to_question(j_data)
            QS.add(q_obj)
    post_questions(server, QS)
    os.chdir(_o_cwd)


if __name__ == '__main__':
    remote_host = "https://wild.gene.ac"
    login(remote_host, 'admin', 'admin')
    list_files_and_upload(remote_host)

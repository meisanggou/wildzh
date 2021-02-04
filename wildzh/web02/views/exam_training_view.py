# !/usr/bin/env python
# coding: utf-8
from zh_config import db_conf_path

from flask import request
from wildzh.utils.async_pool import get_pool
from wildzh.utils import constants
from wildzh.utils import registry
from wildzh.utils.log import getLogger

from wildzh.classes.exam_training import ExamTrainingDetail

from wildzh.web02.view import View2


__author__ = 'zhouhenglc'

LOG = getLogger()
url_prefix = "/exam/training"

exam_training_view = View2("exam_training", __name__, url_prefix=url_prefix)

et_man = ExamTrainingDetail(db_conf_path=db_conf_path)

"""
监听和注册事件
"""
def handle_questions(resource, event, trigger, questions, **kwargs):
    user_no = kwargs['user_no']
    exam_no = kwargs['exam_no']
    for q_item in questions:
        et_man.add_detail(user_no, exam_no, q_item['no'], q_item['state'])

registry.subscribe(handle_questions, constants.R_QUESTION, constants.E_AFTER_UPDATE)


@exam_training_view.route('/tag', methods=['GET'])
def get_question_tag():
    return 'success'

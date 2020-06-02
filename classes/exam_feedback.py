# !/usr/bin/env python
# coding: utf-8
import time

__author__ = 'zhouhenglc'


class ExamQuestionFeedback(object):

    def __init__(self, db):
        self.db = db
        self.cols = ['exam_no', 'user_no', 'question_no', 'fd_type',
                     'description', 'state', 'result', 'times',
                     'update_time']
        self.t = 'exam_question_feedback'

    def select_question_feedback(self, exam_no, user_no=None,
                                 question_no=None, state=None):
        where_value = dict(exam_no=exam_no)
        if user_no:
            where_value['user_no'] = user_no
        if question_no:
            where_value['question_no'] = int(question_no)
        if state is not None:
            where_value['state'] = int(state)
        items = self.db.execute_select(self.t, cols=self.cols,
                                       where_value=where_value)
        return items

    def insert_question_feedback(self, exam_no, user_no, question_no,
                                 fd_type, description):
        state = 0
        u_time = time.time()
        question_no = int(question_no)
        data = dict(exam_no=exam_no, user_no=user_no, question_no=question_no,
                    description=description, state=state, update_time=u_time,
                    times=1, fd_type=fd_type)
        l = self.db.execute_insert(self.t, kwargs=data)
        return l

    def update_question_feedback(self, exam_no, user_no, question_no,
                                 fd_type=None, description=None,
                                 result=None, state=0, times=None):
        question_no = int(question_no)
        where_value = dict(exam_no=exam_no, question_no=question_no,
                           user_no=user_no)
        update_value = dict()
        if fd_type:
            update_value['fd_type'] = fd_type
        if description:
            update_value['description'] = description
        if state > 0:
            update_value['state'] = state
        if result:
            update_value['result'] = result
        if not update_value:
            return 0
        if times is not None:
            if times > 15:
                times = 15
            update_value['times'] = times
        l = self.db.execute_update(self.t, where_value=where_value,
                                   update_value=update_value)
        return l

    def new_or_update_feedback(self, exam_no, user_no, question_no, fd_type,
                               description):
        items = self.select_question_feedback(exam_no, user_no, question_no)
        if len(items) > 0:
            item = items[0]
            times = item['times'] + 1
            l = self.update_question_feedback(exam_no, user_no, question_no,
                                              fd_type=fd_type,
                                              description=description,
                                              times=times)
        else:
            l = self.insert_question_feedback(exam_no, user_no, question_no,
                                              fd_type, description)
        return l

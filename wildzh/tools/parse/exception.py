# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


class ParseException(Exception):

    def __init__(self, text_items, msg):
        if isinstance(text_items, str):
            text_items = [text_items, ]
        self.text_items = text_items
        self.msg = msg


class ParseQuestionException(ParseException):

    def __init__(self, q_items, msg):
        super().__init__(q_items, msg)
        self.q_items = self.text_items


class QuestionNoRepeat(ParseQuestionException):

    def __init__(self, q_items, no):
        msg = '不允许设置重复的题目编号，已存在题目编号：%s' % no
        ParseException.__init__(self, q_items, msg)


class AnswerNotFound(ParseQuestionException):

    def __init__(self, q_items, q_obj=None):
        msg = '没有设置答案'
        self.q_obj = q_obj
        ParseException.__init__(self, q_items, msg)


class InvalidOption(ParseQuestionException):

    def __init__(self, q_items, msg):
        msg = '选项有误：%s' % msg
        ParseException.__init__(self, q_items, msg)


class QuestionTypeNotMatch(ParseQuestionException):

    def __init__(self, q_items, msg):
        ParseException.__init__(self, q_items, msg)


class ParseAnswerError(ParseException):

    def __init__(self, answer_items, msg):
        super().__init__(answer_items, msg)
        self.answer_items = self.text_items

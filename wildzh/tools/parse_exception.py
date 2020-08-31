# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


class ParseException(Exception):

    def __init__(self, q_items, msg):
        self.q_items = q_items
        self.msg = msg


class QuestionNoRepeat(ParseException):

    def __init__(self, q_items, no):
        msg = '不允许设置重复的题目编号，已存在题目编号：%s' % no
        ParseException.__init__(self, q_items, msg)


class AnswerNotFound(ParseException):

    def __init__(self, q_items):
        msg = '没有设置答案'
        ParseException.__init__(self, q_items, msg)


class InvalidOption(ParseException):

    def __init__(self, q_items, msg):
        msg = '选项有误：%s' % msg
        ParseException.__init__(self, q_items, msg)


class QuestionTypeNotMatch(ParseException):

    def __init__(self, q_items, msg):
        ParseException.__init__(self, q_items, msg)

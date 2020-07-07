# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


class ParseException(Exception):

    def __init__(self, q_items, msg):
        self.q_items = q_items
        self.msg = msg


class QuestionNoRepeat(ParseException):

    def __init__(self, q_items, no):
        msg = no
        ParseException.__init__(self, q_items, msg)


class AnswerNotFound(ParseException):

    def __init__(self, q_items, msg):
        ParseException.__init__(self, q_items, msg)


class InvalidOption(ParseException):

    def __init__(self, q_items, msg):
        msg = '选项有误：%s' % msg
        ParseException.__init__(self, q_items, msg)
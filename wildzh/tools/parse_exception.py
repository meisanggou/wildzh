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
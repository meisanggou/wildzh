# !/usr/bin/env python
# coding: utf-8

import re
import sys

from parse_option import ParseOptions


class QuestionType(object):
    Choice = "Choice"
    QA = "Questions and answers"


class ParseQuestion(object):
    option_compile = re.compile("\(?\s*[%s]\s*\)?" % "".join(ParseOptions.option_prefix),
                                re.I)

    def __init__(self):
        self.no = None
        self.options = None
        self._desc = None
        self.answer = None
        self.q_type = None
        self.select_mode = None
        self.inside_mark = None
        self._initialized = False

    @property
    def initialized(self):
        return self._initialized

    def parse(self, question_items):
        if self._initialized:
            raise RuntimeError("initialized")
        if len(question_items) == 0:
            return None
        desc = ""
        q_no = question_items[0]
        i = 1
        while i < len(question_items):
            qs_item = question_items[i]
            if self.option_compile.match(qs_item) is not None:
                break
            desc += qs_item
            i += 1
        parse_o = ParseOptions()
        if i >= len(question_items):
            parse_o.A = u"会"
            parse_o.B = u"不会"
            self.q_type = QuestionType.QA
        else:
            parse_o.parse(question_items[i:])
            self.q_type = QuestionType.Choice
        real_options = parse_o.to_list()
        r_options = map(lambda x: dict(desc=x, score=0), real_options)
        self.no = q_no
        self.desc = desc.strip()
        self.options = parse_o
        self._initialized = True
        return dict(no=q_no, desc=desc, options=r_options)

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        _value = value.strip()
        if not _value:
            raise RuntimeError("Desc length must gt 0")
        self._desc = _value

    def set_answer(self, answer):
        if not self.initialized:
            raise RuntimeError("Question not initialized")
        if self.q_type == QuestionType.Choice:
            if not hasattr(self.options, answer):
                raise RuntimeError("Not Found answer option: %s" % answer)
            getattr(self.options, answer).score = 1
            self.answer = ""
        else:
            self.options.A.score = 1
            self.answer = answer

    def to_dict(self):
        real_options = self.options.to_list()
        return dict(no=self.no, desc=self.desc, options=real_options)

    def to_exam_dict(self):
        _q_item = dict()
        _q_item["question_no"] = self.no
        _q_item['question_desc'] = self.desc
        _q_item['select_mode'] = self.select_mode
        _q_item['options'] = self.options.to_list()
        _q_item['inside_mark'] = self.inside_mark
        _q_item['answer'] = self.answer
        return _q_item


class QuestionSet(object):

    def __init__(self):
        self._s = dict()
        self._select_mode_s = dict()

    def add(self, question):
        if isinstance(question, ParseQuestion):
            raise RuntimeError("Please add ParseQuestion item")
        if question.no in self._s:
            raise RuntimeError("")
        self._s[question.no] = question

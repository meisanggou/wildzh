# !/usr/bin/env python
# coding: utf-8

import collections
import re
import sys

from parse_option import ListOption
from parse_option import ParseOptions


class QuestionType(object):
    Choice = "Choice"
    QA = "Questions and answers"


class ParseQuestion(object):
    _s_of = "".join(ParseOptions.option_prefix)
    option_compile = re.compile("^\s*\(\s*[%s]\s*\)" % _s_of, re.I)  # 匹配 (A)
    option_compile2 = re.compile("^\s*[%s]\s*" % _s_of, re.I)         # 匹配 A

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

    def find_options_location(self, question_items):
        _complies = [self.option_compile, self.option_compile2]
        _c_len = len(_complies)
        location = -1
        use_index = _c_len
        i = 1
        while i < len(question_items):
            qs_item = question_items[i]
            if use_index <= 0:
                break
            for j in range(use_index):
                _c = _complies[j]
                if _c.match(qs_item) is None:
                    continue
                location = i
                use_index = j
                break
            i += 1
        return location

    def parse(self, question_items):
        if self._initialized:
            raise RuntimeError("initialized")
        if len(question_items) == 0:
            return None

        q_no = question_items[0]

        i = self.find_options_location(question_items[:])

        if i < 0:
            desc = "\n".join(question_items[1:])
            options = ListOption(["A", "B"])
            options.A = u"会"
            options.B = u"不会"
            self.q_type = QuestionType.QA

        else:
            desc = "\n".join(question_items[1:i])
            p_data = ParseOptions().parse(question_items[i:])
            if p_data['prefix']:
                desc += "\n" + p_data['prefix']
            options = p_data['options']
            self.q_type = QuestionType.Choice
        real_options = options.to_list()
        r_options = map(lambda x: dict(desc=x, score=0), real_options)
        self.no = q_no
        self.desc = desc.strip()
        self.options = options
        self._initialized = True
        return dict(no=q_no, desc=desc, options=r_options)

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        _value = value.strip()
        if not _value:
            import pdb
            pdb.set_trace()
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
        self.exam_no = None
        self.exam_name = None
        self._s = collections.OrderedDict()
        # self._select_mode_s = dict()

    @property
    def length(self):
        return len(self._s.keys())

    def __len__(self):
        return self.length

    def add(self, question):
        if not isinstance(question, ParseQuestion):
            raise RuntimeError("Please add ParseQuestion item")
        if question.no in self._s:
            raise RuntimeError("")
        self._s[question.no] = question

    def append(self, question):
        return self.add(question)

    def __iter__(self):
        for item in self._s.values():
            yield item

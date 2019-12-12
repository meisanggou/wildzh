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


class Question(object):

    def __init__(self):
        self.no = None
        self.options = None
        self._desc = None
        self.answer = None
        self.q_type = None
        self.select_mode = None
        self.inside_mark = None

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
        if self.answer is not None:
            raise RuntimeError("Has already set answer")
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
        if self.answer is None:
            raise RuntimeError("Net set answer %s" % self.no)
        _q_item = dict()
        _q_item["question_no"] = self.no
        _q_item['question_desc'] = self.desc
        _q_item['select_mode'] = self.select_mode
        _q_item['options'] = self.options.to_list()
        _q_item['inside_mark'] = self.inside_mark
        _q_item['answer'] = self.answer
        return _q_item


class ParseQuestion(object):
    _s_of = "".join(ParseOptions.option_prefix)
    option_compile = re.compile("^\s*\(\s*[%s]\s*\)" % _s_of, re.I)  # 匹配 (A)
    option_compile2 = re.compile("^\s*[%s]\s*" % _s_of, re.I)         # 匹配 A
    answer_compile = re.compile('\(\s*([%s])\s*\)' % _s_of, re.I)
    qa_answer_compile = re.compile(u'(\s*(?:答|答案)(?::|：))', re.I)

    @classmethod
    def find_options_location(cls, question_items):
        _complies = [cls.option_compile, cls.option_compile2]
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

    @classmethod
    def find_one_line_answer(cls, desc):
        items = cls.qa_answer_compile.split(desc)
        if len(items) != 3:
            return desc, ""
        return items[0], items[2]

    @classmethod
    def find_qa_answer(cls, desc):
        n_desc = []
        lines = desc.split("\n")
        if len(lines) == 1:
            return cls.find_one_line_answer(desc)
        index = 0
        answer = ""
        for line in lines:
            m = cls.qa_answer_compile.match(line)
            if m:
                answer = line[len(m.groups()[0]):]
                break
            index += 1
        n_desc = "\n".join(lines[:index])
        answer += "\n".join(lines[index:])
        return n_desc, answer

    @classmethod
    def find_choice_answer(cls, desc):
        _a_num = 1
        answers = []

        def _replace(m):
            answers.append(m.groups()[0])
            return '( )'
        n_desc, num = cls.answer_compile.subn(_replace, desc)
        if num > _a_num:
            raise RuntimeError("Answer num not match")

        return n_desc, answers

    @classmethod
    def find_answer(cls, q_type, desc):
        pass

    @classmethod
    def parse(cls, question_items):
        if len(question_items) == 0:
            return None
        q_no = question_items[0]
        i = cls.find_options_location(question_items[:])
        q = Question()
        if i < 0:
            desc = "\n".join(question_items[1:])
            options = ListOption(["A", "B"])
            options.A = u"会"
            options.B = u"不会"
            q.options = options
            q.q_type = QuestionType.QA
            n_desc, answers = cls.find_qa_answer(desc)
            if len(answers) > 0:
                q.set_answer(answers)
        else:
            desc = "\n".join(question_items[1:i])
            p_data = ParseOptions().parse(question_items[i:])
            if p_data['prefix']:
                desc += "\n" + p_data['prefix']
            q.options = p_data['options']
            q.q_type = QuestionType.Choice
            n_desc, answers = cls.find_choice_answer(desc)
            if len(answers) > 0:
                q.set_answer(answers[0])

        q.no = q_no
        q.desc = n_desc
        return q


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
        if not isinstance(question, Question):
            raise RuntimeError("Please add Question item")
        if question.select_mode not in self._s:
            self._s[question.select_mode] = collections.OrderedDict()
        if question.no in self._s[question.select_mode]:
            raise RuntimeError("")
        self._s[question.select_mode][question.no] = question

    def append(self, question):
        return self.add(question)

    def __iter__(self):
        for items in self._s.values():
            for item in items.values():
                yield item

# !/usr/bin/env python
# coding: utf-8

import collections
import json
import re
import sys

import wildzh.tools.parse_exception as p_exc
from wildzh.tools.parse_option import ListOption
from wildzh.tools.parse_option import ParseOptions


class AnswerLocation(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        value = args[0].lower()
        if value not in cls._instances:
            cls._instances[value] = object.__new__(cls)
        return cls._instances[value]

    def __init__(self, value):
        self.value = value

    @property
    def IAmFile(self):
        return AnswerLocation.is_file(self)

    @classmethod
    def embedded(cls):
        return cls('Embedded')

    @classmethod
    def file(cls):
        return cls('File')

    @classmethod
    def is_embedded(cls, value):
        return value is cls.embedded()

    @classmethod
    def is_file(cls, value):
        return value is cls.file()


class QuestionType(object):
    Choice = "Choice"
    QA = "Questions and answers"


class Question(object):

    def __init__(self, q_items=None):
        self.q_items = q_items
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
        if isinstance(answer, Answer):
            answer = answer.answer
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
        return dict(no=self.no, desc=self.desc, options=real_options,
                    select_mode=self.select_mode, answer=self.answer)

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

    def to_update_dict(self, *keys):
        if self.answer is None:
            raise RuntimeError("Net set answer %s" % self.no)
        _q_item = dict()
        for key in keys:
            _key = key
            if key == 'question_desc':
                _key = 'desc'
            if not hasattr(self, _key):
                raise RuntimeError('No Key %s in %s' % (_key, self))
            _q_item[key] = getattr(self, _key)
            if key == 'options':
                _q_item[key] = _q_item[key].to_list()
        _q_item["question_no"] = self.no
        return _q_item

    def __str__(self):
        return json.dumps(self.to_dict())


class ParseQuestion(object):
    _s_of = "".join(ParseOptions.option_prefix)
    option_compile = re.compile("^\s*\(\s*[%s]\s*\)" % _s_of, re.I)  # 匹配 (A)
    option_compile2 = re.compile("^\s*[%s]\s*" % _s_of, re.I)         # 匹配 A
    answer_compile = re.compile(u'(?:\(|（)\s*([%s])\s*(?:）|\))' % _s_of, re.I)    # 匹配
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
    def find_answer_by_separator(cls, desc, separators):
        p = "|".join([re.escape(s) for s in separators])
        re_p = re.compile("(%s)" % p)
        desc_l = re_p.split(desc, 1)
        if len(desc_l) != 3:
            return desc, ""
        return desc_l[0], desc_l[2]

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
        answer += "\n".join(lines[index + 1:])
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
    def parse(cls, question_items, select_mode=None, embedded_answer=None):
        if len(question_items) == 0:
            return None
        q_no = question_items[0]
        if select_mode in (None, 1):
            i = cls.find_options_location(question_items[:])
        else:
            i = -1
        q = Question(question_items)
        q.no = q_no
        if i < 0:
            desc = "\n".join(question_items[1:])
            options = ListOption(["A", "B"])
            options.A = u"会"
            options.B = u"不会"
            q.options = options
            q.q_type = QuestionType.QA
            if embedded_answer and select_mode == 2:
                # 名词解释
                n_desc, answers = cls.find_answer_by_separator(desc,
                                                               [':', u'：'])
                if len(answers) == 0:
                    raise RuntimeError('Not Found Answer. desc is %s. '
                                       'question is %s' % (desc, q))
                q.set_answer(answers)
            else:
                n_desc, answers = cls.find_qa_answer(desc)
                if len(answers) > 0:
                    q.set_answer(answers)
        else:
            desc = "\n".join(question_items[1:i])
            p_r, p_data = ParseOptions().parse(question_items[i:])
            if p_r is False:
                raise p_exc.InvalidOption(q.q_items, p_data)
            if p_data['prefix']:
                desc += "\n" + p_data['prefix']
            q.options = p_data['options']
            q.q_type = QuestionType.Choice
            n_desc, answers = cls.find_choice_answer(desc)
            if len(answers) > 0:
                q.set_answer(answers[0])
            elif embedded_answer:
                raise p_exc.AnswerNotFound(q.q_items)

        q.desc = n_desc
        return q


class QuestionSet(object):

    def __init__(self, exam_no=None, dry_run=True, **kwargs):
        # self.has_answer = kwargs.pop('has_answer', True)
        self.default_select_mode = kwargs.pop('default_sm', None)
        self.set_source = kwargs.pop('set_source', False)
        self.set_mode = kwargs.pop('set_mode', False)
        self.real_upload = kwargs.pop('real_upload', not dry_run)
        self.answer_location = kwargs.pop('answer_location', '')
        self.set_keys = kwargs.pop('set_keys', ['answer', 'question_desc'])
        self.exam_no = exam_no
        self.exam_name = kwargs.pop('exam_name', None)
        self.dry_run = dry_run
        self._s = collections.OrderedDict()
        self.question_subject = kwargs.pop('question_subject', 0)  # 0-微观经济学 1-宏观经济学 2-政治经济学
        self.inside_mark_prefix = kwargs.pop('inside_mark_prefix', '')
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
            raise p_exc.QuestionNoRepeat(question.q_items, question.no)
        self._s[question.select_mode][question.no] = question

    def append(self, question):
        return self.add(question)

    def __iter__(self):
        for items in self._s.values():
            for item in items.values():
                yield item

    def clear(self):
        self._s.clear()


class ParseAnswer(object):

    def __init__(self, select_mode):
        self.select_mode = select_mode

    def parse(self, answer):
        a = Answer(self.select_mode)
        a.answer = answer
        return a


class Answer(object):

    def __init__(self, select_mode=None):
        self.select_mode = select_mode
        self.no = None
        self._answer = None

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, v):
        if self.select_mode == 1:
            v = v.upper()
            if v not in ["A", "B", "C", "D"]:
                raise RuntimeError("Not Choice Answer %s" % v)
        self._answer = v


class AnswerSet(object):

    def __init__(self):
        self._s = collections.OrderedDict()

    @property
    def length(self):
        return len(self._s.keys())

    def __len__(self):
        return self.length

    def add(self, answer):
        if not isinstance(answer, Answer):
            raise RuntimeError("Please add Answer item")
        if answer.select_mode not in self._s:
            self._s[answer.select_mode] = collections.OrderedDict()
        if answer.no in self._s[answer.select_mode]:
            print(answer)
            import pdb
            pdb.set_trace()
            raise RuntimeError("repeated answers %s" % answer.no)
        self._s[answer.select_mode][answer.no] = answer

    def append(self, answer):
        return self.add(answer)

    def find_answer(self, question):
        _sm = question.select_mode
        if _sm not in self._s:
            return None
        if question.no not in self._s[_sm]:
            return None
        return self._s[_sm][question.no]

    def __iter__(self):
        for items in self._s.values():
            for item in items.values():
                yield item


if __name__ == '__main__':
    e = AnswerLocation('Embedded')
    e2 = AnswerLocation('Embedded')
    e3 = AnswerLocation.embedded()
    print(e is e2)
    print(e2 is e3)
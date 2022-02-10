# !/usr/bin/env python
# coding: utf-8

import collections
import json
import re

import wildzh.tools.parse_exception as p_exc
from wildzh.tools.parse.answer import Answer
from wildzh.tools.parse_option import ListOption
from wildzh.tools.parse_option import ParseOptions


RIGHT_CS = ['对', '√']
WRONG_CS = ['错', '×']


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

    def __str__(self):
        return self.value


class QuestionType(object):
    Choice = "Choice"
    QA = "Questions and answers"
    Judge = "Judgment"


class Question(object):

    def __init__(self, q_items=None):
        self.q_items = q_items
        self._no = None
        self.options = None
        self._desc = None
        self._desc_rs = []
        self._desc_medias = set()
        # 保存文本字符串与 真实煤体资源对应的路径
        self._medias_mapping = {'desc': {}, 'answer': {}, 'options': []}
        self._answer = None
        self.q_type = None
        self.select_mode = None
        self.inside_mark = None
        self.desc_url = None
        self.in_doubt = False
        self._uploaded_medias = []
        # 是否只是测试运行，如果是测试运行，将不真的上传图片
        # 一般有QuestionSet对象在添加Question时添加
        self._dry_run = False

    @property
    def no(self):
        return self._no

    @no.setter
    def no(self, v):
        if isinstance(v, int):
            self._no = v
        else:
            self._no = int(v[:-1])
            self.in_doubt = True

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, values):
        """
        :param values
        case 1: values = value
        case 2: values = value, medias
        medias: {'[[<uuid>]]': <path>, '[[<uuid>]]': <path>, ...}
        :return:
        """
        if isinstance(values, (tuple, list)):
            if len(values) != 2:
                raise RuntimeError('Bad desc value %s' % values)
            value, medias = values
        else:
            value = values
            medias = {}
        _value = value.strip()
        if not _value:
            raise RuntimeError("Desc length must gt 0")
        self._desc = _value
        self._medias_mapping['desc'] = medias

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, values):
        """
        :param values
        case 1: values = value
        case 2: values = value, medias
        medias: {'[[<uuid>]]': <path>, '[[<uuid>]]': <path>, ...}
        :return:
        """
        if isinstance(values, (tuple, list)):
            if len(values) != 2:
                raise RuntimeError('Bad answer value %s' % values)
            value, medias = values
        else:
            value = values
            medias = {}
        _value = value.strip()

        self._answer = _value
        self._medias_mapping['answer'] = medias

    @property
    def dry_run(self):
        return self._dry_run

    @dry_run.setter
    def dry_run(self, v):
        self._dry_run = v

    def set_answer(self, answer):
        # A
        # AD
        # 答案解析
        if self.answer is not None:
            raise RuntimeError("Has already set answer")
        if isinstance(answer, Answer):
            answer = answer.answer
        if self.q_type in (QuestionType.Choice, QuestionType.Judge):
            for opt in answer:
                if not hasattr(self.options, opt):
                    raise p_exc.AnswerNotFound(self.q_items)
                getattr(self.options, opt).score = 1
            self.answer = ""
        else:
            self.options.A.score = 1
            self.answer = answer

    def ensure_has_answer(self):
        if self.answer is None:
            raise p_exc.AnswerNotFound(self.q_items, self)

    def upload_medias(self, func, *args, **kwargs):
        #  问题描述图片
        if self.desc_url and 'desc_url' not in self._uploaded_medias:
            self.desc_url = func(self.desc_url, *args, **kwargs)
            self._uploaded_medias.append(self.desc_url)
        # 问题描述里的图片
        if self._medias_mapping['desc']:
            for key in list(self._medias_mapping['desc'].keys()):
                value = self._medias_mapping['desc'][key]
                n_value = func(value, *args, **kwargs)
                self._desc = self._desc.replace(key, n_value)
                del self._medias_mapping['desc'][key]
        # 答案描述里的图片
        if self._medias_mapping['answer']:
            for key in list(self._medias_mapping['answer'].keys()):
                value = self._medias_mapping['answer'][key]
                n_value = func(value, *args, **kwargs)
                self._answer = self._answer.replace(key, n_value)
                del self._medias_mapping['answer'][key]
        # 选项里的图片
        for option in self.options:
            option.upload_medias(func, *args, **kwargs)

    def to_dict(self):
        real_options = self.options.to_list()
        return dict(no=self.no, desc=self.desc, options=real_options,
                    select_mode=self.select_mode, answer=self.answer,
                    question_desc_url=self.desc_url)

    def to_exam_dict(self, func, *args, **kwargs):
        if self.answer is None:
            raise RuntimeError("Net set answer %s" % self.no)
        self.upload_medias(func, *args, **kwargs)
        _q_item = dict()
        _q_item["question_no"] = self.no
        _q_item['question_desc'] = self.desc
        _q_item['select_mode'] = self.select_mode
        _q_item['options'] = self.options.to_list()
        _q_item['inside_mark'] = self.inside_mark
        _q_item['answer'] = self.answer
        if self.desc_url:
            _q_item['question_desc_url'] = self.desc_url
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

    # 匹配单选或多选答案 匹配中英文括号 括号内包含不可见字符或者 选项A-E 例如：（A） (A) (ABD) ( AB )
    answer_compile = re.compile(u'(?:\(|（)\s*([%s]+)\s*(?:）|\))' % _s_of, re.I)

    # 匹配判断题答案
    j_answer_compile = re.compile(u'(?:\(|（)([\s%s]+)(?:）|\))' % "".join(
        RIGHT_CS + WRONG_CS), re.I)

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
        # 获得问答题 答案
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
    def find_judge_answer(cls, desc):
        _a_num = 1
        answers = []

        def _replace(m):
            c = m.groups()[0]
            if c in RIGHT_CS:
                c = 'A'
            else:
                c = 'B'
            answers.append(c)
            return '( )'
        n_desc, num = cls.j_answer_compile.subn(_replace, desc)
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
        for i in range(len(question_items)):
            question_items[i] = cls.equal_replace(question_items[i])
        q_no = question_items[0]
        if select_mode in (None, 1, 6):  # 1选择题 6 多选题
            i = cls.find_options_location(question_items[:])
            if i < 0 and select_mode in (1, 6):
                raise p_exc.QuestionTypeNotMatch(question_items,
                                                 '题型应该是选择题，未发现选项')
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
                    raise p_exc.AnswerNotFound(question_items)
                q.set_answer(answers)
            elif select_mode == 7:
                # 判断题
                q.q_type = QuestionType.Judge
                options.A = u"正确"
                options.B = u"错误"
                if embedded_answer:
                    n_desc, answers = cls.find_judge_answer(desc)
                    if answers:
                        q.set_answer(answers[0])
                else:
                    n_desc = desc
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

    @classmethod
    def equal_replace(cls, s):
        if not isinstance(s, str):
            return s
        new_s = ''

        for c in s:
            if c in (u"\u3000", u"\xa0"):
                # 替换空白字符
                new_s += ' '
                continue
            oc = ord(c)
            if 65313 <= oc <= 65338:
                # 全角字母 A = 65313 Z = 65338
                # 半角字母 A = 65
                new_s += chr(oc - 65248)
            else:
                new_s += c
        return new_s


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
        self._dry_run = dry_run
        self._s = collections.OrderedDict()
        self.question_subject = kwargs.pop('question_subject', 0)  # 0-微观经济学 1-宏观经济学 2-政治经济学
        self.inside_mark_prefix = kwargs.pop('inside_mark_prefix', '')
        self.inside_mark_fmt = kwargs.pop('inside_mark_fmt', None)
        self._inside_mark_fmt_default = '%(exam_name)s %(question_no)s'
        # self._select_mode_s = dict()

    @property
    def length(self):
        return len(self._s.keys())

    @property
    def dry_run(self):
        return self._dry_run

    @dry_run.setter
    def dry_run(self, v):
        self._dry_run = v
        for q in self:
            q.dry_run = v

    def __len__(self):
        return self.length

    def reset_inside_mark(self):
        for item in self:
            self.set_inside_mark(item)

    def set_inside_mark(self, question):
        fmt = self.inside_mark_fmt or self._inside_mark_fmt_default
        if not self.exam_name and not fmt:
            return
        kwargs = {'exam_name': self.exam_name, 'question_no': question.no}

        mark = fmt % kwargs
        if self.inside_mark_prefix:
            mark = '%s %s' % (self.inside_mark_prefix, mark)
        question.inside_mark = mark

    def _add(self, question):
        question.dry_run = self._dry_run
        self._s[question.select_mode][question.no] = question
        self.set_inside_mark(question)

    def add(self, question):
        if not isinstance(question, Question):
            raise RuntimeError("Please add Question item")
        if question.select_mode not in self._s:
            self._s[question.select_mode] = collections.OrderedDict()
        if question.no in self._s[question.select_mode]:
            if self._s[question.select_mode][question.no].in_doubt:
                # 存疑
                doubt_q = self._s[question.select_mode][question.no]
                if (question.no - 1) in self._s[question.select_mode]:
                    pre_q = self._s[question.select_mode][question.no - 1]
                    _temp = '%s%s' % (doubt_q.no, doubt_q.q_items[1])
                    n_items = pre_q.q_items + [_temp] + doubt_q.q_items[2:]
                    _n_question = ParseQuestion.parse(n_items, question.select_mode)
                    if _n_question:
                        self._add(_n_question)
                        del self._s[question.select_mode][question.no]
            if question.no in self._s[question.select_mode]:
                raise p_exc.QuestionNoRepeat(question.q_items, question.no)
        self._add(question)

    def append(self, question):
        return self.add(question)

    def __iter__(self):
        for items in self._s.values():
            for item in items.values():
                yield item

    def clear(self):
        self._s.clear()

    def ensure_has_answer(self):
        for item in self:
            item.ensure_has_answer()

    def upload_medias(self, func, *args, **kwargs):
        """

        :param func: 方法需要接受 func(path, *args, **kwargs)，返回上传后的路径
        :param args:
        :param kwargs:
        :return:
        """
        if self.dry_run is True and False:
            # if dry_run please set a dummy_func
            return
        for q_item in self:
            q_item.upload_medias(func, *args, **kwargs)
        # TODO 后续考虑将 desc answer中的图片上传也放到这


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

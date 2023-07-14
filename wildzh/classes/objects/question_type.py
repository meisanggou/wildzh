# !/usr/bin/env python
# coding: utf-8
import re

import wildzh.classes.objects.question_answer as q_answer
from wildzh.tools import constants
import wildzh.tools.parse_exception as p_exc
from wildzh.tools.parse_option import ListOption
from wildzh.tools.parse_option import ParseOptions


__author__ = 'zhouhenglc'

G_CH_NUM = ['一', '二', '三', '四', '五', '六', '七', '八', '九']


class QuestionType(object):
    Choice = "Choice"
    QA = "Questions and answers"
    Judge = "Judgment"


class Question(object):
    value = 0
    name = "无"
    alias = []  #  题型的别名
    multi = False  # 是否是多选
    DETECTOR = None
    S_ANSWER_COMP1 = re.compile(r"^(\d+)(.|、|．)([\s\S]*)")
    question_type = None
    answer_cls = q_answer.Answer

    @classmethod
    def reload_detector(cls):
        classes = []
        _cls_q = [Question]
        while _cls_q:
            _cls = _cls_q.pop()
            _cls_q.extend(_cls.__subclasses__())
            classes.extend(_cls.__subclasses__())
        alias = []
        for s_cls in classes:
            alias.append(s_cls.name)
            alias.extend(s_cls.alias)
        # 以中文数字开头，后面直接跟题型 例如 一、选择题
        # 直接以题型开头 例如 选择题
        # 题型后面必须没有字符，或者是不可见字符，或者是中文（，英文(
        com = re.compile("((%s)[、.]|^)(%s)($|\s|（|\()" % (
            "|".join(G_CH_NUM), "|".join(alias)))
        cls.DETECTOR = {'com': com, 'classes': classes}

    @classmethod
    def detection_type(cls, content):
        if not cls.DETECTOR:
            cls.reload_detector()
        classes = cls.DETECTOR['classes']
        com = cls.DETECTOR['com']
        fr = com.findall(content)
        if len(fr) != 1:
            return

        s = fr[0][2]
        for s_cls in classes:
            if s_cls.name == s or s in s_cls.alias:
                return s_cls

    def __init__(self, q_items):
        self.q_items = q_items
        self._no = None
        self.options = None
        self._desc = None
        self._desc_rs = []
        self._desc_medias = set()
        # 保存文本字符串与 真实煤体资源对应的路径
        self._medias_mapping = {'desc': {}, 'answer': {}, 'options': []}
        self._answer = None
        self.q_type = self.question_type
        self.inside_mark = None
        self.desc_url = None
        self.in_doubt = False
        self._uploaded_medias = []
        # 是否只是测试运行，如果是测试运行，将不真的上传图片
        # 一般有QuestionSet对象在添加Question时添加
        self._dry_run = False

    @property
    def select_mode(self):
        return self.value

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
        if isinstance(answer, q_answer.Answer):
            answer = answer.answer
        if self.question_type in (QuestionType.Choice, QuestionType.Judge):
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

    def ensure_no_math(self):
        if constants.MATH_FILL in self.desc:
            raise p_exc.QuestionDescIncludeMath(self.q_items, self)

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

    @classmethod
    def parse(cls, question_items, embedded_answer=None):
        raise RuntimeError('Not Impl')

    @classmethod
    def parse_answers(cls, answer_items):
        ans = cls.answer_cls.parse_answers(answer_items)
        for item in ans:
            item.select_mode = cls.value
        return ans


class ChoiceQuestion(Question):
    value = 1
    name = "选择题"
    alias = ['选择', '单选','单选题', '单项', '单项选择']
    R_VALUES = ["A", "B", "C", "D"]
    #  单选题 答案格式 1-5ADBCD
    S_ANSWER_COMP1 = re.compile(r"(\d+)(?:-|—)(\d+)([a-d]+)", re.I)
    #  单选题 答案格式 1A 2B
    S_ANSWER_COMP2 = re.compile(r"(?:\s|^)(\d+)([a-d](?:\s|$))", re.I)
    question_type = QuestionType.Choice
    # parse
    _s_of = "".join(ParseOptions.option_prefix)
    option_compile = re.compile("^\s*\(\s*[%s]\s*\)" % _s_of, re.I)  # 匹配 (A)
    option_compile2 = re.compile("^\s*[%s]\s*" % _s_of, re.I)         # 匹配 A
    # 匹配单选或多选答案 匹配中英文括号 括号内包含不可见字符或者 选项A-E 例如：（A） (A) (ABD) ( AB )
    answer_compile = re.compile(u'(?:\(|（)\s*([%s]+)\s*(?:）|\))' % _s_of, re.I)
    answer_cls = q_answer.ChoiceAnswer

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
    def parse(cls, question_items, embedded_answer=None):
        if len(question_items) == 0:
            return None
        for i in range(len(question_items)):
            question_items[i] = cls.equal_replace(question_items[i])
        q_no = question_items[0]
        i = cls.find_options_location(question_items[:])
        if i < 0:
            raise p_exc.QuestionTypeNotMatch(question_items,
                                             '题型应该是选择题，未发现选项')
        q = cls(question_items)
        q.no = q_no
        desc = "\n".join(question_items[1:i])
        p_r, p_data = ParseOptions().parse(question_items[i:])
        if p_r is False:
            raise p_exc.InvalidOption(q.q_items, p_data)
        if p_data['prefix']:
            desc += "\n" + p_data['prefix']
        q.options = p_data['options']
        n_desc, answers = cls.find_choice_answer(desc)
        if len(answers) > 0:
            q.set_answer(answers[0])
        elif embedded_answer:
            raise p_exc.AnswerNotFound(q.q_items)
        q.desc = n_desc
        return q


class MCJSQuestion(Question):
    value = 2
    name = "名词解释"
    alias = []
    question_type = QuestionType.QA
    answer_cls = q_answer.QAAnswer

    @classmethod
    def find_answer_by_separator(cls, desc, separators):
        p = "|".join([re.escape(s) for s in separators])
        re_p = re.compile("(%s)" % p)
        desc_l = re_p.split(desc, 1)
        if len(desc_l) != 3:
            return desc, ""
        return desc_l[0], desc_l[2]

    @classmethod
    def parse(cls, question_items, embedded_answer=None):
        if len(question_items) == 0:
            return None
        for i in range(len(question_items)):
            question_items[i] = cls.equal_replace(question_items[i])
        q_no = question_items[0]
        q = cls(question_items)
        q.no = q_no
        desc = "\n".join(question_items[1:])
        options = ListOption(["A", "B"])
        options.A = u"会"
        options.B = u"不会"
        q.options = options
        if embedded_answer:
            # 名词解释
            n_desc, answers = cls.find_answer_by_separator(
                desc, [':', u'：'])
            if len(answers) == 0:
                raise p_exc.AnswerNotFound(question_items)
            q.set_answer(answers)
        else:
            n_desc = desc
        q.desc = n_desc
        return q


class JDQuestion(MCJSQuestion):
    value = 3
    name = "简答题"
    alias = ['简答']
    qa_answer_compile = re.compile(u'(\s*(?:答|答案)(?::|：))', re.I)

    @classmethod
    def find_one_line_answer(cls, desc):
        items = cls.qa_answer_compile.split(desc)
        if len(items) != 3:
            return desc, ""
        return items[0], items[2]

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
    def parse(cls, question_items, embedded_answer=None):
        if len(question_items) == 0:
            return None
        for i in range(len(question_items)):
            question_items[i] = cls.equal_replace(question_items[i])
        q_no = question_items[0]
        q = cls(question_items)
        q.no = q_no
        desc = "\n".join(question_items[1:])
        q.desc = desc
        options = ListOption(["A", "B"])
        options.A = u"会"
        options.B = u"不会"
        q.options = options
        if embedded_answer:
            n_desc, answers = cls.find_qa_answer(desc)
            if len(answers) > 0:
                q.set_answer(answers)
            q.desc = n_desc
        return q


class JSQuestion(JDQuestion):
    value = 4
    name = "计算题"
    alias = ['计算']


class LSQuestion(JDQuestion):
    value = 5
    name = "论述题"
    alias = ['论述']


class MultiChoiceQuestion(ChoiceQuestion):
    value = 6
    name = "多选题"
    alias = ['多选']
    multi = True
    R_VALUES = ["A", "B", "C", "D", 'E', 'F']
    #  多选题 答案格式 1.ABC 2、BE 3AB
    S_ANSWER_COMP1 = re.compile(r"(?:\s|^)(\d+)(?:\.|、)([a-f]+(?:\s|$))",
                                re.I)
    answer_cls = q_answer.MultiChoiceAnswer


class JudgeQuestion(Question):
    value = 7
    name = "判断题"
    alias = ['判断']
    RIGHT_CS = ['对', '√']
    WRONG_CS = ['错', '×']
    #  判断题 答案格式 1-5×√×√√
    S_ANSWER_COMP1 = re.compile(r"(\d+)(?:-|—)(\d+)([×√]+)", re.I)
    #  判断题 答案格式 1× 2√
    S_ANSWER_COMP2 = re.compile(r"(?:\s|^)(\d+)([×√](?:\s|$))", re.I)
    question_type = QuestionType.Judge
    # 匹配判断题答案
    j_answer_compile = re.compile(u'(?:\(|（)([\s%s]+)(?:）|\))' % "".join(
        RIGHT_CS + WRONG_CS), re.I)
    answer_cls = q_answer.JudgeAnswer

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
    def parse(cls, question_items, select_mode=None, embedded_answer=None):
        if len(question_items) == 0:
            return None
        for i in range(len(question_items)):
            question_items[i] = cls.equal_replace(question_items[i])
        q_no = question_items[0]
        q = cls(question_items)
        q.no = q_no
        desc = "\n".join(question_items[1:])
        options = ListOption(["A", "B"])
        options.A = u"会"
        options.B = u"不会"
        q.options = options
        # 判断题
        options.A = u"正确"
        options.B = u"错误"
        if embedded_answer:
            n_desc, answers = cls.find_judge_answer(desc)
            if answers:
                q.set_answer(answers[0])
        else:
            n_desc = desc
        q.desc = n_desc
        return q


class WordMeaningQuestion(JDQuestion):
    value = 8
    name = "单词释义"
    alias = []
    @classmethod
    def parse(cls, question_items, select_mode=None, embedded_answer=None):
        if len(question_items) == 0:
            return None
        for i in range(len(question_items)):
            question_items[i] = cls.equal_replace(question_items[i])
        q_no = question_items[0]
        q = cls(question_items)
        q.no = q_no

        desc = "\n".join(question_items[1:])
        options = ListOption(["A", "B"])
        options.A = u"会"
        options.B = u"不会"
        q.options = options
        # 单词释义
        if embedded_answer:
            n_desc = question_items[1]
            q.set_answer("\n".join(question_items[2:]))
        else:
            n_desc = desc
        q.desc = n_desc
        return q


# G_OPTION_TYPE = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题", "多选题", "判断题"]
G_OPTION_TYPE = [Question]
_cls_q = [Question]
while _cls_q:
    _cls = _cls_q.pop()
    _cls_q.extend(_cls.__subclasses__())
    G_OPTION_TYPE.extend(_cls.__subclasses__())
G_OPTION_TYPE.sort(key=lambda x: x.value)
G_QUESTION_CLS = G_OPTION_TYPE


if __name__ == '__main__':
    print(JudgeQuestion.name)

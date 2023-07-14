# !/usr/bin/env python
# coding: utf-8
import re
from wildzh.tools.parse import exception

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

    @classmethod
    def reload_detector(cls):
        classes = []
        classes.extend(cls.__subclasses__())
        alias = []
        for s_cls in classes:
            alias.append(s_cls.name)
            alias.extend(s_cls.alias)
        # 以中文数字开头，后面直接跟题型 例如 一、选择题
        # 直接以题型开头 例如 选择题
        # 题型后面必须没有字符，或者是不可见字符，或者是中文（
        com = re.compile("((%s)[、.]|^)(%s)($|\s|（)" % (
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

    def __init__(self, v):
        self.no = None
        self._answer = None
        if v:
            self.answer = v

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, v):
        self._answer = v

    @classmethod
    def parse_answers(cls, answer_items):
        aw_dict = []
        current_no = -1
        current_answer = ""
        answer_items = map(lambda x: x.strip(), answer_items)
        one_items = []
        for item in answer_items:
            # 判断是否是答案开始
            found_items = cls.S_ANSWER_COMP1.findall(item)
            if found_items:
                found_item = found_items[0]
                next_no = int(found_item[0])
                if next_no < current_no:
                    # 不允许出现同一个答案区域，出现题号下降。防止答案里出现小题题号，出现误判
                    current_answer += "\n" + item
                    continue
                if next_no >= current_no + 10 and current_no > 0:
                    # 不允许出现同一个答案区域，出现题号上升过快
                    current_answer += "\n" + item
                    continue
                if current_no != -1:
                    if current_no in aw_dict:
                        raise exception.ParseAnswerError(
                            one_items, "重复的答案 %s" % current_no)
                    a = cls(current_answer)
                    a.no = current_no
                    aw_dict.append(a)
                current_no = next_no
                current_answer = found_item[2]
                one_items = [item]
            else:
                current_answer += "\n" + item
                one_items.append(item)
        if current_no != -1:
            a = cls(current_answer)
            a.no = current_no
            aw_dict.append(a)
        return aw_dict


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

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, v):
        v = v.upper().strip()
        if v not in self.R_VALUES:
            raise RuntimeError("Not %s %s" % (self.__class__.__name__, v))
        self._answer = v

    @classmethod
    def parse_answers(cls, answer_items):
        aw_dict = []
        for a_item in answer_items:
            sp_items = cls.S_ANSWER_COMP1.findall(a_item)
            for start, end, answers in sp_items:
                i_start, i_end = int(start), int(end)
                if len(answers) != i_end - i_start + 1:
                    raise exception.ParseAnswerError(
                        a_item, "不是正确的格式：%s-%s%s" % (start, end, answers))
                for i in range(i_start, i_end + 1):
                    if i in aw_dict:
                        raise exception.ParseAnswerError(
                            a_item, "重复的答案 %s" % i)
                    a = cls(answers[i - i_start])
                    a.no = i
                    aw_dict.append(a)
            sp_items2 = cls.S_ANSWER_COMP2.findall(a_item)
            for no, answer in sp_items2:
                a = cls(answer)
                a.no = int(no)
                aw_dict.append(a)
        return aw_dict


class MCJSQuestion(Question):
    value = 2
    name = "名词解释"
    alias = []
    question_type = QuestionType.QA


class JDQuestion(Question):
    value = 3
    name = "简答题"
    alias = ['简答']
    question_type = QuestionType.QA


class JSQuestion(Question):
    value = 4
    name = "计算题"
    alias = ['计算']
    question_type = QuestionType.QA


class LSQuestion(Question):
    value = 5
    name = "论述题"
    alias = ['论述']
    question_type = QuestionType.QA


class MultiChoiceQuestion(Question):
    value = 6
    name = "多选题"
    alias = ['多选']
    multi = True
    R_VALUES = ["A", "B", "C", "D", 'E', 'F']
    #  多选题 答案格式 1.ABC 2、BE 3AB
    S_ANSWER_COMP1 = re.compile(r"(?:\s|^)(\d+)(?:\.|、)([a-f]+(?:\s|$))",
                                re.I)
    question_type = QuestionType.Choice

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, v):
        v = v.upper().strip()
        for c in v:
            if c not in self.R_VALUES:
                raise RuntimeError("Not %s %s" % (self.__class__.__name__, v))
        self._answer = v

    @classmethod
    def parse_answers(cls, answer_items):
        aw_dict = []
        for a_item in answer_items:
            sp_items3 = cls.S_ANSWER_COMP1.findall(a_item)
            for no, answer in sp_items3:
                a = cls(answer)
                a.no = int(no)
                aw_dict.append(a)
        return aw_dict


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

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, v):
        if v in self.RIGHT_CS:
            v = 'A'
        elif v in self.WRONG_CS:
            v = 'B'
        else:
            raise RuntimeError("Not %s %s" % (self.__class__.__name__, v))
        self._answer = v

    @classmethod
    def parse_answers(cls, answer_items):
        aw_dict = []
        for a_item in answer_items:
            sp_items = cls.S_ANSWER_COMP1.findall(a_item)
            for start, end, answers in sp_items:
                i_start, i_end = int(start), int(end)
                if len(answers) != i_end - i_start + 1:
                    raise exception.ParseAnswerError(
                        a_item, "不是正确的格式：%s-%s%s" % (start, end, answers))
                for i in range(i_start, i_end + 1):
                    if i in aw_dict:
                        raise exception.ParseAnswerError(
                            a_item, "重复的答案 %s" % i)
                    a = cls(answers[i - i_start])
                    a.no = i
                    aw_dict.append(a)
            sp_items2 = cls.S_ANSWER_COMP2.findall(a_item)
            for no, answer in sp_items2:
                a = cls(answer)
                a.no = int(no)
                aw_dict.append(a)
        return aw_dict


class WordMeaningQuestion(Question):
    value = 8
    name = "单词释义"
    alias = []
    question_type = QuestionType.QA


# G_OPTION_TYPE = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题", "多选题", "判断题"]

G_OPTION_TYPE = [Question] + sorted(Question.__subclasses__(),
                                      key=lambda x: x.value)
G_QUESTION_CLS = G_OPTION_TYPE


if __name__ == '__main__':
    print(JudgeQuestion.name)

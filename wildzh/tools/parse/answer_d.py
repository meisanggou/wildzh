# !/usr/bin/env python
# coding: utf-8
import re

from wildzh.tools.parse import exception

__author__ = 'zhouhenglc'


class Answer(object):
    SELECT_MODE = 0
    S_ANSWER_COMP1 = re.compile(r"^(\d+)(.|、|．)([\s\S]*)")

    def __init__(self, v):
        self.no = None
        self._answer = None
        if v:
            self.answer = v

    @property
    def select_mode(self):
        return self.SELECT_MODE

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, v):
        self._answer = v

    @classmethod
    def get_parser(cls, select_mode):
        if select_mode == Answer.SELECT_MODE:
            return Answer
        for s_cls in Answer.__subclasses__():
            if s_cls.SELECT_MODE == select_mode:
                return s_cls
        raise RuntimeError('Not Support select_mode %s' % select_mode)

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


class ChoiceAnswer(Answer):
    SELECT_MODE = 1
    R_VALUES = ["A", "B", "C", "D"]
    S_ANSWER_COMP1 = re.compile(r"(\d+)(?:-|—)(\d+)([a-d]+)", re.I)  #  单选题 答案格式 1-5ADBCD
    S_ANSWER_COMP2 = re.compile(r"(?:\s|^)(\d+)([a-d](?:\s|$))", re.I)  #  单选题 答案格式 1A 2B

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


class MCJSAnswer(Answer):
    SELECT_MODE = 2


class JDAnswer(Answer):
    SELECT_MODE = 3


class JSAnswer(Answer):
    SELECT_MODE = 4


class LSAnswer(Answer):
    SELECT_MODE = 5


class MultiChoiceAnswer(Answer):
    SELECT_MODE = 6
    R_VALUES = ["A", "B", "C", "D", 'E', 'F']
    S_ANSWER_COMP1 = re.compile(r"(?:\s|^)(\d+)(?:\.|、)([a-f]+(?:\s|$))", re.I)  #  多选题 答案格式 1.ABC 2、BE 3AB

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


class JudgeAnswer(Answer):
    SELECT_MODE = 7
    RIGHT_CS = ['对', '√']
    WRONG_CS = ['错', '×']
    S_ANSWER_COMP1 = re.compile(r"(\d+)(?:-|—)(\d+)([×√]+)", re.I)  #  判断题 答案格式 1-5×√×√√
    S_ANSWER_COMP2 = re.compile(r"(?:\s|^)(\d+)([×√](?:\s|$))", re.I)  #  判断题 答案格式 1× 2√

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


if __name__ == '__main__':
    print(JudgeAnswer.get_parser(1))

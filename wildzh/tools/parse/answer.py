# !/usr/bin/env python
# coding: utf-8

__author__ = 'zhouhenglc'

G_SELECT_MODE = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题", "多选题", "判断题"]


class Answer(object):
    SELECT_MODE = 0

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
    def parse(cls, select_mode, v=None):
        if select_mode == cls.SELECT_MODE:
            return cls(v)
        for s_cls in cls.__subclasses__():
            if s_cls.SELECT_MODE == select_mode:
                return s_cls(v)
        raise RuntimeError('Not Support select_mode %s' % select_mode)


class ChoiceAnswer(Answer):
    SELECT_MODE = 1
    R_VALUES = ["A", "B", "C", "D"]

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, v):
        v = v.upper().strip()
        if v not in self.R_VALUES:
            raise RuntimeError("Not %s %s" % (self.__class__.__name__, v))
        self._answer = v


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


class JudgeAnswer(Answer):
    SELECT_MODE = 7
    RIGHT_CS = ['对', '√']
    WRONG_CS = ['错', '×']

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


if __name__ == '__main__':
    print(Answer.__subclasses__())

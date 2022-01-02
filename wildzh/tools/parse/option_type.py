# !/usr/bin/env python
# coding: utf-8
import re

__author__ = 'zhouhenglc'

G_CH_NUM = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
G_OPTION_TYPE = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题", "多选题", "判断题"]


class OptionType(object):
    value = 0
    name = G_OPTION_TYPE[value]
    alias = []
    DETECTOR = None

    @classmethod
    def reload_detector(cls):
        classes = [OptionType]
        classes.extend(OptionType.__subclasses__())
        alias = []
        for s_cls in classes:
            alias.append(s_cls.name)
            alias.extend(s_cls.alias)
        com = re.compile(u"((%s)[、.]|^)(%s)" % (
            "|".join(G_CH_NUM), "|".join(alias)))
        cls.DETECTOR = {'com': com, 'classes': classes}

    @classmethod
    def detection_type(cls, content):
        if not cls.DETECTOR:
            cls.reload_detector()
        classes = cls.DETECTOR['classes']
        com = cls.DETECTOR['com']
        classes.extend(OptionType.__subclasses__())
        fr = com.findall(content)
        if len(fr) != 1:
            return -1

        s = fr[0][2]
        for s_cls in classes:
            if s_cls.name == s or s in s_cls.alias:
                return s_cls.value


class ChoiceOptionType(OptionType):
    value = 1
    name = G_OPTION_TYPE[value]
    alias = ['选择', '单选','单选题', '单项', '单项选择']


class MCJSOptionType(OptionType):
    value = 2
    name = G_OPTION_TYPE[value]
    alias = []


class JDOptionType(OptionType):
    value = 3
    name = G_OPTION_TYPE[value]
    alias = ['简答']


class JSOptionType(OptionType):
    value = 4
    name = G_OPTION_TYPE[value]
    alias = ['计算']


class LSOptionType(OptionType):
    value = 5
    name = G_OPTION_TYPE[value]
    alias = ['论述']


class MultiChoiceOptionType(OptionType):
    value = 6
    name = G_OPTION_TYPE[value]
    alias = ['多选']


class JudgeOptionType(OptionType):
    value = 7
    name = G_OPTION_TYPE[value]
    alias = ['判断']


if __name__ == '__main__':
    print(JudgeOptionType.name)

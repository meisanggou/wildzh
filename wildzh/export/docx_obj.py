# !/usr/bin/env python
# coding: utf-8
import os
import jinja2

from wildzh.utils import constants

__author__ = 'zhouhenglc'


abs_dir = os.path.abspath(os.path.dirname(__file__))
temp_dir = os.path.join(abs_dir, 'docx_template')

_ENV = jinja2.Environment()



class XmlObj(object):
    temp_name = ""
    temp_str = None
    env = _ENV

    def __new__(cls, *args, **kwargs):
        if cls.temp_str is None:
            temp_path = os.path.join(temp_dir, cls.temp_name)
            if not temp_path.endswith('.template'):
                temp_path += '.template'
            with open(temp_path, encoding=constants.ENCODING) as r:
                cls.temp_str = r.read()
        return object.__new__(cls)

    def __init__(self):
        pass

    @classmethod
    def transfer(cls, s):
        _d = ["&", "&amp;", "<", "&lt;", ">", "&gt;", "'", "&apos;",
              '"', '&quot;']
        for i in range(0, len(_d), 2):
            s = s.replace(_d[i], _d[i + 1])
        return s

    def _to_xml(self, **kwargs):
        t = self.env.from_string(self.temp_str)
        r = t.render(**kwargs)
        return r

    def to_xml(self):
        return self._to_xml()


class ParagraphXmlObj(XmlObj):
    temp_name = 'paragraph'

    def __init__(self, runs=None, **kwargs):
        """
        outline_level new support 1 2, if add should update word/styles.xml
        """
        super().__init__()
        self._runs = []
        self._outline_level = None

        self.runs = runs
        self.outline_level = kwargs.get('outline_level', None)

    @property
    def runs(self):
        return self._runs

    @runs.setter
    def runs(self, runs):
        self._runs = []
        kwargs = {}
        if self.outline_level:
            kwargs['font_size'] = None
        if isinstance(runs, str):
            self._runs.append(RunTextXmlObj(runs, **kwargs))
        elif isinstance(runs, (list, tuple)):
            for run in runs:
                if isinstance(run, dict) and 'url' in run:
                    self._runs.append(RunImageXmlObj(run))
                else:
                    self._runs.append(RunTextXmlObj(run, **kwargs))

    @property
    def outline_level(self):
        return self._outline_level

    @outline_level.setter
    def outline_level(self, v):
        self._outline_level = v
        if self._outline_level:
            for run in self.runs:
                run.font_size = None

    def to_xml(self):
        runs = [x.to_xml() for x in self._runs]
        kwargs = {'runs': runs, 'outline_level': self.outline_level}
        return self._to_xml(**kwargs)


class ParagraphPageXmlObj(XmlObj):
    temp_name = 'paragraph_page'


class RunTextXmlObj(XmlObj):
    temp_name = 'run_text'

    def __init__(self, text, font_size=24):
        super().__init__()
        self.text = text
        self.font_size = font_size

    def to_xml(self):
        kwargs = {'text': self.transfer(self.text),
                  'font_size': self.font_size}
        return self._to_xml(**kwargs)


class RunImageXmlObj(XmlObj):
    temp_name = 'run_image'

    def __init__(self, item):
        super().__init__()
        self.item = item

    def to_xml(self):
        return self._to_xml(**self.item)


class BlockParent(object):
    MODES = []

    @classmethod
    def subclass(cls):
        cs = []
        for c in cls.__subclasses__():
            cs.append(c)
            if hasattr(c, 'subclass'):
                cs.extend(c.subclass())
        return cs

    def __new__(cls, *args, **kwargs):
        mode = args[0]
        cs = cls.subclass()
        new_cls = cls
        for c in cs:
            if mode in c.MODES:
                new_cls = c
                break
        return super().__new__(new_cls)

    def __init__(self, mode, questions, answer_mode):
        self.mode = mode
        self.answer_mode = answer_mode
        self.questions = questions

    def _get_alone_answers(self):
        return self._get_alone_detail_answers()

    def _get_alone_detail_answers(self):
        return []

    def get_answers(self):
        if self.answer_mode == 'alone':
            ps = self._get_alone_answers()
        else:
            ps = self._get_alone_detail_answers()
        return [p.to_xml() for p in ps]


class Block(BlockParent):
    MODES = [2, 3, 4, 5, ]

    def _get_alone_answers(self):
        return self._get_alone_detail_answers()

    def _get_alone_detail_answers(self):
        ss_paragraphs = []
        for q_item in self.questions:
            if q_item['multi_answer_rich']:
                q_item['multi_answer_rich'][0].insert(
                    0, '%s、' % q_item['this_question_no'])
            for ar in q_item['multi_answer_rich']:
                ss_paragraphs.append(ParagraphXmlObj(ar))
        return ss_paragraphs


class SingleChoiceBlock(Block):
    MODES = [1, ]
    @staticmethod
    def get_right_option(question):
        return question['right_option']

    def _get_alone_answers(self):
        ss_paragraphs = [[]]
        ss_item = []
        i = 0
        for item in self.questions:
            item['right_option'] = self.get_right_option(item)
            ss_item.append(item)
            i += 1
            if i % 5 == 0:
                rp = '%s-%s %s  ' % (
                    ss_item[0]['this_question_no'],
                    ss_item[-1]['this_question_no'],
                    ''.join([x['right_option'] for x in ss_item]))
                ss_paragraphs[-1].append(rp)
                if i % 20 == 0:
                    ss_paragraphs.append([])
                ss_item = []
        if ss_item:
            rp = '%s-%s %s' % (ss_item[0]['this_question_no'],
                               ss_item[-1]['this_question_no'],
                               ''.join([x['right_option'] for x in ss_item]))
            ss_paragraphs[-1].append(rp)
        return [ParagraphXmlObj(p) for p in ss_paragraphs]

    def _get_alone_detail_answers(self):
        ss_paragraphs = []
        for item in self.questions:
            right_option = self.get_right_option(item)
            pa = '%s.%s' % (item['this_question_no'], right_option)
            ss_paragraphs.append(pa)
            details = ['解析：']
            details.extend(item['answer_rich'])
            ss_paragraphs.append(details)
        return [ParagraphXmlObj(p) for p in ss_paragraphs]


class MultipleChoiceBlock(SingleChoiceBlock):
    MODES = [6, ]
    def _get_alone_answers(self):
        ss_paragraphs = [[]]
        i = 0
        for item in self.questions:
            p = '%s %s ' % (item['this_question_no'], item['right_option'])
            ss_paragraphs[-1].append(p)
            i += 1
            if i % 5 == 0:
                ss_paragraphs.append([])
        return [ParagraphXmlObj(p) for p in ss_paragraphs]


class JudgeBlock(SingleChoiceBlock):
    MODES = [7, ]

    @staticmethod
    def get_right_option(question):
        if question['options'][0]['score'] > 0:
            return '√'
        return '×'


if __name__ == '__main__':
    px = ParagraphXmlObj()
    print(BlockParent(6, [], 'alone'))

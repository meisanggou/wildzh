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
        kwargs = {'text': self.text, 'font_size': self.font_size}
        return self._to_xml(**kwargs)


class RunImageXmlObj(XmlObj):
    temp_name = 'run_image'

    def __init__(self, item):
        super().__init__()
        self.item = item

    def to_xml(self):
        return self._to_xml(**self.item)


if __name__ == '__main__':
    px = ParagraphXmlObj()

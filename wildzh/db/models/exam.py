# !/usr/bin/env python
# coding: utf-8
import json
import sqlalchemy
from wildzh.db.models import Base

__author__ = 'zhouhenglc'


class ExamOpennessLevel(object):
    PRIVATE = 'private'
    SEMI_PUBLIC = 'semi-public'
    PUBLIC = 'public'


class ExamInfoModel(Base):

    __tablename__ = 'exam_info'

    exam_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    exam_name = sqlalchemy.Column(sqlalchemy.CHAR(50))
    exam_desc = sqlalchemy.Column(sqlalchemy.CHAR(2000), default=0)
    exam_extend = sqlalchemy.Column(sqlalchemy.TEXT(), default=0)
    status = sqlalchemy.Column(sqlalchemy.INT(), default=0)
    exam_num = sqlalchemy.Column(sqlalchemy.INT(), default=0)
    adder = sqlalchemy.Column(sqlalchemy.CHAR(30))
    question_num = sqlalchemy.Column(sqlalchemy.INT())

    @property
    def _extend(self):
        if not hasattr(self, '__extend'):
            if self.exam_extend:
                self.__extend = json.loads(self.exam_extend)
            else:
                self.__extend = self.exam_extend
        return self.__extend

    @property
    def openness_level(self):
        if not hasattr(self, '_openness_level'):
            if self._extend and 'openness_level' in self._extend:
                self._openness_level = self._extend['openness_level']
            else:
                self._openness_level = ExamOpennessLevel.PRIVATE
        return self._openness_level

    def is_private(self):
        return self.openness_level == ExamOpennessLevel.PRIVATE

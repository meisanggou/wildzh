# !/usr/bin/env python
# coding: utf-8
import json
import sqlalchemy
from sqlalchemy.dialects.mysql import BIT
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
    exam_desc = sqlalchemy.Column(sqlalchemy.CHAR(2000))
    exam_extend = sqlalchemy.Column(sqlalchemy.TEXT())
    status = sqlalchemy.Column(sqlalchemy.INT())
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


class ExamMemberFlowModel(Base):
    __tablename__ = 'exam_member_flow'

    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    exam_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    update_time = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    exam_role = sqlalchemy.Column(sqlalchemy.INT())
    authorizer = sqlalchemy.Column(sqlalchemy.INT())
    end_time = sqlalchemy.Column(sqlalchemy.INT())


class ExamGenStrategyModel(Base):

    __tablename__ =  'exam_gen_strategy'
    exam_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    strategy_id = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    strategy_name = sqlalchemy.Column(sqlalchemy.VARCHAR(32))
    strategy_items = sqlalchemy.Column(sqlalchemy.VARCHAR(500))
    internal = sqlalchemy.Column(BIT())
    update_time = sqlalchemy.Column(sqlalchemy.INT())


class ExamQuestionFeedback(Base):
    __tablename__ =  'exam_question_feedback'
    exam_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    user_no = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    insert_time = sqlalchemy.Column(sqlalchemy.INT(), primary_key=True)
    question_no = sqlalchemy.Column(sqlalchemy.INT())
    fb_type = sqlalchemy.Column(sqlalchemy.VARCHAR(30))
    description = sqlalchemy.Column(sqlalchemy.VARCHAR(200))
    state = sqlalchemy.Column(sqlalchemy.SMALLINT())
    result = sqlalchemy.Column(sqlalchemy.VARCHAR(50), default="")
    times = sqlalchemy.Column(sqlalchemy.SMALLINT())
    update_time = sqlalchemy.Column(sqlalchemy.INT())


class ExamBatchEvent(Base):
    __tablename__ =  'exam_batch_events'
    batch_id = sqlalchemy.Column(sqlalchemy.CHAR(32), primary_key=True)
    exam_no = sqlalchemy.Column(sqlalchemy.INT())
    batch_type = sqlalchemy.Column(sqlalchemy.VARCHAR(30))
    batch_data = sqlalchemy.Column(sqlalchemy.VARCHAR(500))
    create_time = sqlalchemy.Column(sqlalchemy.INT())
    update_time = sqlalchemy.Column(sqlalchemy.INT())

# !/usr/bin/env python
# coding: utf-8
from sqlalchemy.ext import declarative
from sqlalchemy.orm import object_mapper

__author__ = 'zhouhenglc'


class _Base(object):

    @declarative.declared_attr
    def __tablename__(self):
        lower_name = self.__name__.lower()
        if lower_name.endswith('model'):
            lower_name = lower_name[:-5]
        return lower_name + 's'

    def save(self, session):
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def to_dict(self):
        columns = list(dict(object_mapper(self).columns).keys())
        return {c: getattr(self, c) for c in columns}


Base = declarative.declarative_base(cls=_Base)

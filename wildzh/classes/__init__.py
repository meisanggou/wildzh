# !/usr/bin/env python
# coding: utf-8
import time
import uuid

from mysqldb_rich.db2 import DB

__author__ = 'meisa'


class BaseObject(object):
    model = None
    uuid_col = None

    @property
    def now_time(self):
        return time.time()

    def query(self, session, **kwargs):
        query = session.query(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query

    def create(self, session, **kwargs):
        if hasattr(self.model, 'update_time'):
            kwargs['update_time'] = self.now_time
        if hasattr(self.model, 'add_time'):
            kwargs['add_time'] = self.now_time
        if self.uuid_col:
            kwargs[self.uuid_col] = uuid.uuid4()
        obj = self.model(**kwargs)
        obj.save(session)
        return obj

    def get_all(self, session, **kwargs):
        return session.query(self.model).filter_by(**kwargs).all()

    def update(self, session, where_value, **kwargs):
        kwargs['internal'] = 1 if kwargs['internal'] else 0
        return session.query(self.model).filter_by(**where_value).update(
            kwargs)

    def delete(self, session, **kwargs):
        return session.query(self.model).filter_by(**kwargs).delete()


class DBObject(object):
    table = None
    columns = []

    def __init__(self, db=None, db_conf_path=None):
        if db is None:
            db = DB(db_conf_path)
        self.db = db
        self.t = self.table
        self.cols = self.columns

    @property
    def now_time(self):
        return time.time()

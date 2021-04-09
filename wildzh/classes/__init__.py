# !/usr/bin/env python
# coding: utf-8
import time
from mysqldb_rich.db2 import DB

__author__ = 'meisa'


class BaseObject(object):
    model = None

    @property
    def now_time(self):
        return time.time()

    def create(self, session, **kwargs):
        obj = self.model(**kwargs)
        obj.save(session)
        return obj

    def get_all(self, session, **kwargs):
        return session.query(self.model).filter_by(**kwargs).all()


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

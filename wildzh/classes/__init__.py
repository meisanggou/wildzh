# !/usr/bin/env python
# coding: utf-8
from mysqldb_rich.db2 import DB

__author__ = 'meisa'


class DBObject(object):
    table = None
    columns = []

    def __init__(self, db=None, db_conf_path=None):
        if db is None:
            db = DB(db_conf_path)
        self.db = db
        self.t = self.table
        self.cols = self.columns

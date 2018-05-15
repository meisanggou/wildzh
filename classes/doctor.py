# !/usr/bin/env python
# coding: utf-8

from mysqldb_rich import DB

__author__ = 'meisa'


class Doctor(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t = "docker_info"
        self.t_detail = "doctor_detail"

    def _insert_info(self):
        pass

    def _insert_detail(self):
        pass
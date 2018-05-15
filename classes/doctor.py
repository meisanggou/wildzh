# !/usr/bin/env python
# coding: utf-8

import time
import uuid
from mysqldb_rich import DB

__author__ = 'meisa'


class Doctor(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t = "doctor_info"
        self.t_detail = "doctor_detail"

    def _insert_info(self, doctor_name, degree, company, department, domain, star_level, service_times, labels):
        kwargs = dict(doctor_name=doctor_name, degree=degree, company=company, department=department, domain=domain,
                      star_level=star_level, service_times=service_times, labels=labels)
        kwargs["doctor_no"] = uuid.uuid4().hex
        kwargs["insert_time"] = int(time.time())
        self.db.execute_insert(self.t, kwargs)
        return kwargs

    def _insert_detail(self, doctor_profile, work_experience, study_experience, honor, unit_price):
        kwargs = dict(doctor_profile=doctor_profile, work_experience=work_experience, study_experience=study_experience,
                      honor=honor, unit_price=unit_price)
        l = self.db.execute_insert(self.t_detail, kwargs)
        return l

    def _update_status(self, music_no, add_status=None, sub_status=None):
        where_value = dict(music_no=music_no)
        if add_status is not None:
            l = self.db.execute_logic_or(self.t, status=add_status, where_value=where_value)
        elif sub_status is not None:
            l = self.db.execute_logic_non(self.t, where_value=where_value, status=sub_status)
        else:
            l = 0
        return l

    def _update_num(self, music_no):
        where_value = dict(music_no=music_no)
        l = self.db.execute_plus(self.t, "service_times", where_value=where_value)
        return l

    def select_doctor(self):
        cols = ["doctor_no", "doctor_name", "degree", "company", "department", "domain", "star_level",
                "service_times", "labels", "insert_time"]
        items = self.db.execute_select(self.t, cols=cols)
        return items

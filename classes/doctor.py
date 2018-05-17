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

    def _insert_info(self, doctor_name, doctor_photo, degree, company, department, domain, star_level, service_times,
                     labels):
        kwargs = dict(doctor_name=doctor_name, degree=degree, company=company, department=department, domain=domain,
                      star_level=star_level, service_times=service_times, labels=labels, doctor_photo=doctor_photo)
        kwargs["doctor_no"] = uuid.uuid4().hex
        kwargs["insert_time"] = int(time.time())
        self.db.execute_insert(self.t, kwargs)
        return kwargs

    def _insert_detail(self, doctor_no, doctor_profile, work_experience, study_experience, honor, unit_price):
        kwargs = dict(doctor_profile=doctor_profile, work_experience=work_experience, study_experience=study_experience,
                      honor=honor, unit_price=unit_price, doctor_no=doctor_no)
        l = self.db.execute_insert(self.t_detail, kwargs)
        return l

    def _update_info(self, doctor_no, **kwargs):
        where_value = dict(doctor_no=doctor_no)
        l = self.db.execute_update(self.t, update_value=kwargs, where_value=where_value)
        return l

    def _update_detail(self, doctor_no, **kwargs):
        where_value = dict(doctor_no=doctor_no)
        l = self.db.execute_update(self.t_detail, update_value=kwargs, where_value=where_value)
        return l

    def _update_status(self, doctor_no, add_status=None, sub_status=None):
        where_value = dict(doctor_no=doctor_no)
        if add_status is not None:
            l = self.db.execute_logic_or(self.t, status=add_status, where_value=where_value)
        elif sub_status is not None:
            l = self.db.execute_logic_non(self.t, where_value=where_value, status=sub_status)
        else:
            l = 0
        return l

    def _update_num(self, doctor_no):
        where_value = dict(doctor_no=doctor_no)
        l = self.db.execute_plus(self.t, "service_times", where_value=where_value)
        return l

    def new_info(self, doctor_name, doctor_photo, degree, company, department, domain, star_level, labels):
        service_times = 0
        item = self._insert_info(doctor_name, doctor_photo, degree, company, department, domain, star_level,
                                 service_times, labels)
        return item

    def new_detail(self, doctor_no, doctor_profile, work_experience, study_experience, honor, unit_price):
        l = self._insert_detail(doctor_no, doctor_profile, work_experience, study_experience, honor, unit_price)
        self._update_status(doctor_no, add_status=2)
        return l

    def update_doctor(self, doctor_no, **kwargs):
        cols = ["doctor_name", "degree", "company", "department", "domain", "star_level", "labels"]
        for key in kwargs.keys():
            if kwargs[key] is None or key not in cols:
                del kwargs[key]
        return self._update_info(doctor_no, **kwargs)

    def update_detail(self, doctor_no, **kwargs):
        cols = ["doctor_profile", "work_experience", "study_experience", "honor", "unit_price"]
        for key in kwargs.keys():
            if kwargs[key] is None or key not in cols:
                del kwargs[key]
        return self._update_detail(doctor_no, **kwargs)

    def select_doctor(self, doctor_no=None):
        if doctor_no is not None:
            where_value = dict(doctor_no=doctor_no)
        else:
            where_value = None
        cols = ["doctor_no", "doctor_name", "degree", "company", "department", "domain", "star_level",
                "service_times", "labels", "insert_time", "doctor_photo", "status"]
        items = self.db.execute_select(self.t, cols=cols, where_value=where_value)
        return items

    def select_detail(self, doctor_no):
        cols = ["doctor_no", "doctor_profile", "work_experience", "study_experience", "honor", "unit_price"]
        where_value = dict(doctor_no=doctor_no)
        items = self.db.execute_select(self.t_detail, cols=cols, where_value=where_value)
        if len(items) <= 0:
            return None
        return items[0]

    def online_doctor(self, doctor_no):
        l = self._update_status(doctor_no, add_status=64)
        return l

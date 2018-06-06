# !/usr/bin/env python
# coding: utf-8

import time
import uuid
from mysqldb_rich import DB

__author__ = 'meisa'


class People(object):

    def __init__(self, db_conf_path):
        self.db = DB(conf_path=db_conf_path)
        self.t = "people_info"
        self.t_detail = "people_detail"

    def _insert_info(self, people_name, people_photo, degree, company, department, domain, star_level, service_times,
                     labels):
        kwargs = dict(people_name=people_name, degree=degree, company=company, department=department, domain=domain,
                      star_level=star_level, service_times=service_times, labels=labels, people_photo=people_photo)
        kwargs["people_no"] = uuid.uuid4().hex
        kwargs["insert_time"] = int(time.time())
        self.db.execute_insert(self.t, kwargs)
        return kwargs

    def _insert_detail(self, people_no, people_profile, tel, work_experience, study_experience, honor, unit_price):
        kwargs = dict(people_profile=people_profile, work_experience=work_experience, study_experience=study_experience,
                      honor=honor, unit_price=unit_price, people_no=people_no, tel=tel)
        l = self.db.execute_insert(self.t_detail, kwargs)
        return l

    def _update_info(self, people_no, **kwargs):
        where_value = dict(people_no=people_no)
        l = self.db.execute_update(self.t, update_value=kwargs, where_value=where_value)
        return l

    def _update_detail(self, people_no, **kwargs):
        where_value = dict(people_no=people_no)
        l = self.db.execute_update(self.t_detail, update_value=kwargs, where_value=where_value)
        return l

    def _update_status(self, people_no, add_status=None, sub_status=None):
        where_value = dict(people_no=people_no)
        if add_status is not None:
            l = self.db.execute_logic_or(self.t, status=add_status, where_value=where_value)
        elif sub_status is not None:
            l = self.db.execute_logic_non(self.t, where_value=where_value, status=sub_status)
        else:
            l = 0
        return l

    def _update_num(self, people_no):
        where_value = dict(people_no=people_no)
        l = self.db.execute_plus(self.t, "service_times", where_value=where_value)
        return l

    def new_info(self, people_name, people_photo, degree, company, department, domain, star_level, labels):
        service_times = 0
        item = self._insert_info(people_name, people_photo, degree, company, department, domain, star_level,
                                 service_times, labels)
        return item

    def new_detail(self, people_no, people_profile, tel, work_experience, study_experience, honor, unit_price):
        l = self._insert_detail(people_no, people_profile, tel, work_experience, study_experience, honor, unit_price)
        self._update_status(people_no, add_status=2)
        return l

    def update_people(self, people_no, **kwargs):
        cols = ["people_name", "people_photo", "degree", "company", "department", "domain", "star_level",
                "labels"]
        for key in kwargs.keys():
            if kwargs[key] is None or key not in cols:
                del kwargs[key]
        return self._update_info(people_no, **kwargs)

    def update_detail(self, people_no, **kwargs):
        cols = ["people_profile", "tel", "work_experience", "study_experience", "honor", "unit_price"]
        for key in kwargs.keys():
            if kwargs[key] is None or key not in cols:
                del kwargs[key]
        return self._update_detail(people_no, **kwargs)

    def select_people(self, people_no=None):
        where_cond = ["status<>0"]
        if people_no is not None:
            where_value = dict(people_no=people_no)
        else:
            where_value = None
        cols = ["people_no", "people_name", "degree", "company", "department", "domain", "star_level",
                "service_times", "labels", "insert_time", "people_photo", "status"]
        items = self.db.execute_select(self.t, cols=cols, where_value=where_value, where_cond=where_cond)
        for item in items:
            for k, v in item.items():
                k = k.replace("people", "doctor")
                item[k] = v
        return items

    def select_detail(self, people_no, add_times=False):
        cols = ["people_no", "people_profile", "tel", "work_experience", "study_experience", "honor",
                "unit_price"]
        where_value = dict(people_no=people_no)
        items = self.db.execute_select(self.t_detail, cols=cols, where_value=where_value)
        if len(items) <= 0:
            return None
        for item in items:
            for k, v in item.items():
                k = k.replace("people", "doctor")
                item[k] = v
        if add_times is True:
            self._update_num(people_no)
        return items[0]

    def online_people(self, people_no):
        l = self._update_status(people_no, add_status=64)
        return l

    def delete_people(self, people_no):
        l = self._update_info(people_no, status=0)
        return l

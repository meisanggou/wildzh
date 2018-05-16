#! /usr/bin/env python
# coding: utf-8

import os
import re
from time import time
from functools import wraps
from flask import request, g, jsonify
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, upload_folder, file_prefix_url
from classes.doctor import Doctor
from web01 import create_blue

__author__ = 'ZhouHeng'

url_prefix = "/doctor"

rt = RenderTemplate("doctor", url_prefix=url_prefix)
doctor_view = create_blue('doctor_view', url_prefix=url_prefix, menu_list={"title": u"医生管理"})
c_doctor = Doctor(db_conf_path)


def referer_doctor_no(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Referer" not in request.headers:
            g.ref_url = ""
            g.doctor_no = None
            return f(*args, **kwargs)
        g.ref_url = request.headers["Referer"]
        find_no = re.findall("doctor_no=(\\w+)", g.ref_url)
        if len(find_no) > 0:
            g.doctor_no = find_no[0]
        elif "doctor_no" in request.args:
            g.doctor_no = request.args["doctor_no"]
        else:
            g.doctor_no = None
        return f(*args, **kwargs)
    return decorated_function


def required_doctor_no(f):
    @wraps(f)
    @referer_doctor_no
    def decorated_function(*args, **kwargs):
        if g.doctor_no is None:
            return jsonify({"status": False, "data": "Bad Request"})
        return f(*args, **kwargs)
    return decorated_function


@doctor_view.route("/", methods=["GET"])
def add_func():
    page_list = url_prefix + "/"
    page_doctor = url_prefix + "/?action=doctor"
    info_url = url_prefix + "/info/"
    upload_url = url_prefix + "/upload/"
    detail_url = url_prefix + "/detail/"
    online_url = url_prefix + "/online/"
    if "action" in request.args and request.args["action"] == "doctor":
        return rt.render("add.html", page_list=page_list, upload_url=upload_url, info_url=info_url)
    elif "action" in request.args and request.args["action"] == "detail":
        return rt.render("detail.html", page_list=page_list, page_doctor=page_doctor, detail_url=detail_url)
    elif "action" in request.args and request.args["action"] == "update":
        return rt.render("update.html", page_list=page_list, page_doctor=page_doctor, info_url=info_url)
    return rt.render("overview.html", info_url=info_url, page_doctor=page_doctor, online_url=online_url)


@doctor_view.route("/info/", methods=["GET"])
@referer_doctor_no
def get_doctor_info():
    items = c_doctor.select_doctor(g.doctor_no)
    return jsonify({"status": True, "data": items})


support_upload2(doctor_view, upload_folder, file_prefix_url, ("doctor", "photo"), "upload")


@doctor_view.route("/info/", methods=["POST"])
def add_doctor_action():
    request_data = request.json
    doctor_name = request_data["doctor_name"]
    doctor_photo = request_data["doctor_photo"]
    degree = request_data["degree"]
    company = request_data["company"]
    domain = request_data["domain"]
    department = request_data["department"]
    star_level = request_data["star_level"]
    labels = request_data["labels"]
    data = c_doctor.new_info(doctor_name, doctor_photo, degree, company, department, domain, star_level, labels)
    return jsonify({"status": True, "data": data})


@doctor_view.route("/info/", methods=["PUT"])
@required_doctor_no
def update_doctor_action():
    request_data = request.json
    c_doctor.update_doctor(g.doctor_no, **request_data)
    request_data["doctor_no"] = g.doctor_no
    return jsonify({"status": True, "data": request_data})


@doctor_view.route("/detail/", methods=["GET"])
@required_doctor_no
def get_detail():
    item = c_doctor.select_detail(g.doctor_no)
    return jsonify({"status": True, "data": [item]})


@doctor_view.route("/detail/", methods=["POST"])
@required_doctor_no
def add_detail_action():
    request_data = request.json
    doctor_profile = request_data["doctor_profile"]
    work_experience = request_data["work_experience"]
    study_experience = request_data["study_experience"]
    honor = request_data["honor"]
    unit_price = request_data["unit_price"]
    l = c_doctor.new_detail(g.doctor_no, doctor_profile, work_experience, study_experience, honor, unit_price)
    request_data["doctor_no"] = g.doctor_no
    return jsonify({"status": True, "data": request_data})


@doctor_view.route("/detail/", methods=["PUT"])
@required_doctor_no
def update_detail_action():
    request_data = request.json
    c_doctor.update_detail(g.doctor_no, **request_data)
    request_data["doctor_no"] = g.doctor_no
    return jsonify({"status": True, "data": request_data})


@doctor_view.route("/online/", methods=["POST"])
def online_music():
    doctor_no = g.request_data["doctor_no"]
    items = c_doctor.select_doctor(doctor_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "医生不存在"})
    c_doctor.online_doctor(doctor_no)
    return jsonify({"status": True, "data": "success"})
#! /usr/bin/env python
# coding: utf-8

import os
import re
from time import time
from functools import wraps
from flask import request, g, jsonify
from flask_login import login_required
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, upload_folder, file_prefix_url
from classes.people import People
from web01 import create_blue

__author__ = 'ZhouHeng'

url_prefix = "/people"

rt = RenderTemplate("people", url_prefix=url_prefix)
doctor_view = create_blue('doctor_view', url_prefix=url_prefix, menu_list={"title": u"医生管理"},
                          auth_required=False)
c_doctor = People(db_conf_path)


def referer_people_no(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Referer" not in request.headers:
            g.ref_url = ""
        else:
            g.ref_url = request.headers["Referer"]
        find_no = re.findall("(people|doctor)_no=(\\w+)", g.ref_url)
        if len(find_no) > 0:
            g.people_no = find_no[0][1]
        elif "people_no" in request.args:
            g.people_no = request.args["people_no"]
        elif "doctor_no" in request.args:
            g.people_no = request.args["doctor_no"]
        else:
            g.people_no = None
        g.doctor_no = g.people_no
        return f(*args, **kwargs)
    return decorated_function


def required_people_no(f):
    @wraps(f)
    @referer_people_no
    def decorated_function(*args, **kwargs):
        if g.doctor_no is None:
            return jsonify({"status": False, "data": "Bad Request"})
        return f(*args, **kwargs)
    return decorated_function


@doctor_view.route("/", methods=["GET"])
@login_required
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
        return rt.render("update.html", page_list=page_list, page_doctor=page_doctor, info_url=info_url,
                         upload_url=upload_url)
    return rt.render("overview.html", info_url=info_url, page_doctor=page_doctor, online_url=online_url)


@doctor_view.route("/info/", methods=["GET"])
@referer_people_no
def get_doctor_info():
    items = c_doctor.select_people(g.people_no)
    if g.user_no is None:
        for i in range(len(items) - 1, -1, -1):
            if items[i]["status"] & 64 == 64:
                continue
            del items[i]
    return jsonify({"status": True, "data": items})


support_upload2(doctor_view, upload_folder, file_prefix_url, ("doctor", "photo"), "upload")


@doctor_view.route("/info/", methods=["POST"])
def add_doctor_action():
    request_data = request.json
    people_name = request_data["people_name"]
    people_photo = request_data["people_photo"]
    degree = request_data["degree"]
    company = request_data["company"]
    domain = request_data["domain"]
    department = request_data["department"]
    star_level = request_data["star_level"]
    labels = request_data["labels"]
    data = c_doctor.new_info(people_name, people_photo, degree, company, department, domain, star_level, labels)
    return jsonify({"status": True, "data": data})


@doctor_view.route("/info/", methods=["PUT"])
@required_people_no
def update_doctor_action():
    request_data = request.json
    c_doctor.update_people(g.doctor_no, **request_data)
    request_data["doctor_no"] = g.doctor_no
    return jsonify({"status": True, "data": request_data})


@doctor_view.route("/info/", methods=["DELETE"])
def delete_doctor_action():
    request_data = request.json
    c_doctor.delete_people(request_data["people_no"])
    return jsonify({"status": True, "data": request_data})


@doctor_view.route("/detail/", methods=["GET"])
@required_people_no
def get_detail():
    items = c_doctor.select_people(g.people_no)
    if len(items) <= 0:
        return jsonify({"status": False, "data": "医生不存在"})
    doctor_item = items[0]
    item = c_doctor.select_detail(g.doctor_no)
    if item is None:
        return jsonify({"status": True, "data": "医生不存在详细信息"})
    doctor_item.update(item)
    if g.user_no is None:
        return jsonify({"status": True, "data": doctor_item})
    return jsonify({"status": True, "data": [doctor_item]})


@doctor_view.route("/detail/tel/", methods=["GET"])
@required_people_no
def get_detail_tel():
    item = c_doctor.select_detail(g.doctor_no, add_times=True)
    if item is None:
        return jsonify({"status": True, "data": "医生不存在详细信息"})
    return jsonify({"status": True, "data": item["tel"]})


@doctor_view.route("/detail/", methods=["POST"])
@required_people_no
def add_detail_action():
    request_data = request.json
    doctor_profile = request_data["doctor_profile"]
    tel = request_data["tel"]
    work_experience = request_data["work_experience"]
    study_experience = request_data["study_experience"]
    honor = request_data["honor"]
    unit_price = request_data["unit_price"]
    l = c_doctor.new_detail(g.doctor_no, doctor_profile, tel, work_experience, study_experience, honor, unit_price)
    request_data["doctor_no"] = g.doctor_no
    return jsonify({"status": True, "data": request_data})


@doctor_view.route("/detail/", methods=["PUT"])
@required_people_no
def update_detail_action():
    request_data = request.json
    c_doctor.update_detail(g.doctor_no, **request_data)
    request_data["doctor_no"] = g.doctor_no
    return jsonify({"status": True, "data": [request_data]})


@doctor_view.route("/online/", methods=["POST"])
def online_music():
    doctor_no = g.request_data["doctor_no"]
    items = c_doctor.select_doctor(doctor_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "医生不存在"})
    c_doctor.online_doctor(doctor_no)
    return jsonify({"status": True, "data": "success"})
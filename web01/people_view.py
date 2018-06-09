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
people_view = create_blue('people_view', url_prefix=url_prefix, menu_list={"title": u"人员管理"},
                          auth_required=False)
c_people = People(db_conf_path)


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
        return f(*args, **kwargs)
    return decorated_function


def required_people_no(f):
    @wraps(f)
    @referer_people_no
    def decorated_function(*args, **kwargs):
        if g.people_no is None:
            return jsonify({"status": False, "data": "Bad Request"})
        return f(*args, **kwargs)
    return decorated_function


@people_view.route("/", methods=["GET"])
@login_required
def add_func():
    page_list = url_prefix + "/?group_id=doctor"
    page_people = url_prefix + "/?action=people&group_id=doctor"
    info_url = url_prefix + "/info/"
    upload_url = url_prefix + "/upload/"
    detail_url = url_prefix + "/detail/"
    online_url = url_prefix + "/online/"
    if "action" in request.args and request.args["action"] == "people":
        return rt.render("add.html", page_list=page_list, upload_url=upload_url, info_url=info_url)
    elif "action" in request.args and request.args["action"] == "detail":
        return rt.render("detail.html", page_list=page_list, page_people=page_people, detail_url=detail_url)
    elif "action" in request.args and request.args["action"] == "update":
        return rt.render("update.html", page_list=page_list, page_people=page_people, info_url=info_url,
                         upload_url=upload_url)
    return rt.render("overview.html", info_url=info_url, page_people=page_people, online_url=online_url)


@people_view.route("/info/", methods=["GET"])
@referer_people_no
def get_people_info():
    if g.people_no is not None:
        items = c_people.select_people(g.people_no)
    elif "group_id" in request.args:
        items = c_people.select_group_people(request.args["group_id"])
    else:
        items = c_people.select_people(None)
    if g.user_no is None or "online" in request.args:
        for i in range(len(items) - 1, -1, -1):
            if items[i]["status"] & 64 == 64:
                continue
            del items[i]
    return jsonify({"status": True, "data": items})


support_upload2(people_view, upload_folder, file_prefix_url, ("people", "photo"), "upload")


@people_view.route("/info/", methods=["POST"])
def add_people_action():
    request_data = request.json
    people_name = request_data["people_name"]
    people_photo = request_data["people_photo"]
    degree = request_data["degree"]
    company = request_data["company"]
    domain = request_data["domain"]
    department = request_data["department"]
    star_level = request_data["star_level"]
    labels = request_data["labels"]
    group_id = request_data.get("group_id", None)
    data = c_people.new_info(people_name, people_photo, degree, company, department, domain, star_level, labels,
                             group_id)
    return jsonify({"status": True, "data": data})


@people_view.route("/info/", methods=["PUT"])
@required_people_no
def update_people_action():
    request_data = request.json
    c_people.update_people(g.people_no, **request_data)
    request_data["people_no"] = g.people_no
    return jsonify({"status": True, "data": request_data})


@people_view.route("/info/", methods=["DELETE"])
def delete_people_action():
    request_data = request.json
    c_people.delete_people(request_data["people_no"])
    return jsonify({"status": True, "data": request_data})


@people_view.route("/detail/", methods=["GET"])
@required_people_no
def get_detail():
    items = c_people.select_people(g.people_no)
    if len(items) <= 0:
        return jsonify({"status": False, "data": "医生不存在"})
    people_item = items[0]
    item = c_people.select_detail(g.people_no)
    if item is None:
        return jsonify({"status": True, "data": "医生不存在详细信息"})
    people_item.update(item)
    if g.user_no is None:
        return jsonify({"status": True, "data": people_item})
    return jsonify({"status": True, "data": [people_item]})


@people_view.route("/detail/tel/", methods=["GET"])
@required_people_no
def get_detail_tel():
    item = c_people.select_detail(g.people_no, add_times=True)
    if item is None:
        return jsonify({"status": True, "data": "医生不存在详细信息"})
    return jsonify({"status": True, "data": item["tel"]})


@people_view.route("/detail/", methods=["POST"])
@required_people_no
def add_detail_action():
    request_data = request.json
    people_profile = request_data["people_profile"]
    tel = request_data["tel"]
    work_experience = request_data["work_experience"]
    study_experience = request_data["study_experience"]
    honor = request_data["honor"]
    unit_price = request_data["unit_price"]
    l = c_people.new_detail(g.people_no, people_profile, tel, work_experience, study_experience, honor, unit_price)
    request_data["people_no"] = g.people_no
    return jsonify({"status": True, "data": request_data})


@people_view.route("/detail/", methods=["PUT"])
@required_people_no
def update_detail_action():
    request_data = request.json
    c_people.update_detail(g.people_no, **request_data)
    request_data["people_no"] = g.people_no
    request_data["people_no"] = g.people_no
    return jsonify({"status": True, "data": [request_data]})


@people_view.route("/online/", methods=["POST"])
def online_people():
    people_no = g.request_data["people_no"]
    items = c_people.select_people(people_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "医生不存在"})
    c_people.online_people(people_no)
    return jsonify({"status": True, "data": "success"})

@people_view.route("/resource/", methods=["GET"])
@required_people_no
def list_people_resource_action():
    items = c_people.select_resource(g.people_no)
    resources = map(lambda x: x["resource_id"], items)
    return jsonify({"status": True, "data": resources})


@people_view.route("/resource/", methods=["POST"])
def add_resource():
    data = g.request_data
    people_no = data["people_no"]
    resource_id = data["resource_id"]
    l = c_people.add_resource(people_no, resource_id)
    return jsonify({"status": True, "data": l})

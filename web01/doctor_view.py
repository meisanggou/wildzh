#! /usr/bin/env python
# coding: utf-8

import os
from time import time
from flask import request, g, jsonify
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, upload_folder, file_prefix_url
from classes.doctor import Doctor
from web01 import create_blue, upload_folder

__author__ = 'ZhouHeng'

url_prefix = "/doctor"

rt = RenderTemplate("doctor", url_prefix=url_prefix)
doctor_view = create_blue('doctor_view', url_prefix=url_prefix, menu_list={"title": u"医生管理"})
c_doctor = Doctor(db_conf_path)


@doctor_view.route("/", methods=["GET"])
def add_func():
    page_list = url_prefix + "/"
    page_doctor = url_prefix + "/?action=doctor"
    info_url = url_prefix + "/info/"
    if "action" in request.args and request.args["action"] == "doctor":
        return rt.render("add.html", page_list=page_list)
    return rt.render("overview.html", info_url=info_url, page_doctor=page_doctor)


@doctor_view.route("/info/", methods=["GET"])
def get_doctor_info():
    items = c_doctor.select_doctor()
    return jsonify({"status": True, "data": items})


@doctor_view.route("/", methods=["POST"])
def add_doctor_action():
    g.user_name = "zh_test"
    request_data = request.json
    title = request_data["title"]
    abstract = request_data["abstract"]
    content = request_data["content"]
    doctor_desc = request_data["doctor_desc"]
    pic_url = request_data["pic_url"]
    exec_r, data = c_doctor.new_doctor(g.user_name, title, abstract, content, doctor_desc, pic_url)
    return jsonify({"status": exec_r, "data": data})


@doctor_view.route("/", methods=["PUT"])
def update_doctor_action():
    request_data = request.json
    doctor_no = request_data["doctor_no"]
    title = request_data["title"]
    abstract = request_data["abstract"]
    content = request_data["content"]
    doctor_desc = request_data["doctor_desc"]
    pic_url = request_data["pic_url"]
    auto = request_data.get("auto", False)
    if auto is False:
        exec_r, data = c_doctor.update_doctor(doctor_no, title, abstract, content, doctor_desc, pic_url)
    else:
        doctor_file = os.path.join(upload_folder, "%s_%s.txt" % (doctor_no, int(time())))
        with open(doctor_file, "w") as wa:
            wa.write(content.encode("utf-8"))
        exec_r, data = True, doctor_file
    return jsonify({"status": exec_r, "data": data})


@doctor_view.route("/query/", methods=["GET"])
def query_func():
    if request.is_xhr is True:
        exec_r, doctors = c_doctor.query_doctor()
        return jsonify({"status": exec_r, "data": doctors})
    url_add_doctor = url_prefix + "/"
    return rt.render("query.html", url_add_doctor=url_add_doctor)

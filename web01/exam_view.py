# !/usr/bin/env python
# coding: utf-8
import os
import re
import string
from flask import request, jsonify, g
from flask_helper import RenderTemplate, support_upload
from zh_config import db_conf_path, upload_folder
from tools import folder
from classes.exam import Exam
from web01 import create_blue

__author__ = 'meisa'

url_prefix = "/exam"

rt = RenderTemplate("exam")
exam_view = create_blue("exam", url_prefix=url_prefix)
c_exam = Exam(db_conf_path)
exam_upload_folder = os.path.join(upload_folder, "exam")
pic_folder = folder.create_folder2(exam_upload_folder, "pic")


@exam_view.route("/", methods=["GET"])
def index():
    add_url = url_prefix + "/"
    upload_url = url_prefix + "/upload/"
    info_url = url_prefix + "/info/"
    if "exam_no" in request.args:
        overview_class = ""
        question_class = "active"
    else:
        overview_class = "active"
        question_class = ""
    return rt.render("index.html", add_url=add_url, overview_class=overview_class, question_class=question_class,
                     upload_url=upload_url, info_url=info_url)


@exam_view.route("/", methods=["POST"])
def new_exam():
    g.user_name = "zh_test"
    data = g.request_data
    r, exam_no = c_exam.new_exam(data["exam_name"], data["exam_type"], data["exam_desc"], data["eval_type"],
                                 g.user_name, pic_url=data["pic_url"])
    if r is False:
        return jsonify({"status": False, "data": "请重试"})
    cases = dict()
    for i in range(len(data["result_explain"])):
        cases["case_%s" % string.letters[i]] = data["result_explain"][i]
    l = c_exam.new_exam_result_explain(exam_no, **cases)
    if l <= 0:
        return jsonify({"status": False, "data": "请重试"})
    data["exam_no"] = exam_no
    return jsonify({"status": True, "data": data})


support_upload(exam_view, static_folder=pic_folder)


@exam_view.route("/info/", methods=["GET"])
def get_exam_info():
    if "Referer" not in request.headers:
            return jsonify({"status": False, "data": "Bad Request"})
    ref_url = request.headers["Referer"]
    find_type = re.findall("exam_type=(\\w+)", ref_url)
    if len(find_type) > 0:
        exam_type = find_type[0]
    elif "exam_type" in request.args:
        exam_type = request.args["exam_type"]
    else:
        return jsonify({"status": False, "data": "Bad Request."})
    find_no = re.findall("exam_no=(\\d+)", ref_url)
    print(find_no)
    if len(find_no) > 0:
        exam_no = find_no[0]
    elif "exam_no" in request.args:
        exam_no = request.args["exam_no"]
    else:
        exam_no = None
    items = c_exam.select_exam(exam_type, exam_no)
    return jsonify({"status": True, "data": items})



# !/usr/bin/env python
# coding: utf-8
import os
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
    if "exam_no" in request.args:
        overview_class = ""
        question_class = "active"
    else:
        overview_class = "active"
        question_class = ""
    return rt.render("index.html", add_url=add_url, overview_class=overview_class, question_class=question_class,
                     upload_url=upload_url)


@exam_view.route("/", methods=["POST"])
def new_exam():
    data = g.request_data
    r, exam_no = c_exam.new_exam(data["exam_name"], data["exam_type"], data["exam_desc"], data["eval_type"],
                                 g.user_name, pic_url=data["pic_url"])
    if r is False:
        return jsonify({"status": False, "data": "请重试"})
    return jsonify({"status": True, "data": data})


support_upload(exam_view, static_folder=pic_folder)


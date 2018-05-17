# !/usr/bin/env python
# coding: utf-8
import os
import re
import string
from functools import wraps
from flask import request, jsonify, g
from flask_login import login_required
from flask_helper import RenderTemplate, support_upload
from zh_config import db_conf_path, upload_folder
from tools import folder
from classes.exam import Exam
from web01 import create_blue

__author__ = 'meisa'

url_prefix = "/exam"

rt = RenderTemplate("exam")
exam_view = create_blue("exam", url_prefix=url_prefix, auth_required=False, menu_list={"title": u"测试管理"})
c_exam = Exam(db_conf_path)
exam_upload_folder = os.path.join(upload_folder, "exam")
pic_folder = folder.create_folder2(exam_upload_folder, "pic")


def referer_exam_no(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Referer" not in request.headers:
            g.ref_url = ""
            g.exam_no = None
            return f(*args, **kwargs)
        g.ref_url = request.headers["Referer"]
        find_no = re.findall("exam_no=(\\d+)", g.ref_url)
        if len(find_no) > 0:
            g.exam_no = find_no[0]
        elif "exam_no" in request.args:
            g.exam_no = request.args["exam_no"]
        else:
            g.exam_no = None
        return f(*args, **kwargs)
    return decorated_function


def required_exam_no(f):
    @wraps(f)
    @referer_exam_no
    def decorated_function(*args, **kwargs):
        if g.exam_no is None:
            return jsonify({"status": False, "data": "Bad Request"})
        return f(*args, **kwargs)
    return decorated_function


@login_required
@exam_view.route("/", methods=["GET"])
def index():
    add_url = url_prefix + "/"
    upload_url = url_prefix + "/upload/"
    info_url = url_prefix + "/info/"
    online_url = url_prefix + "/online/"
    explain_url = url_prefix + "/explain/"
    questions_url = url_prefix + "/questions/"
    page_exam = url_prefix + "/?action=exam"
    page_list = url_prefix + "/"
    if "action" in request.args and request.args["action"] == "exam":
        if "exam_no" in request.args:
            return rt.render("update_info.html", page_list=page_list, page_exam=page_exam, info_url=info_url,
                             upload_url=upload_url, explain_url=explain_url)
        return rt.render("entry_info.html", page_list=page_list, add_url=add_url, upload_url=upload_url)
    if "exam_no" in request.args:
        return rt.render("entry_questions.html", page_list=page_list, page_exam=page_exam, info_url=info_url,
                         questions_url=questions_url)
    return rt.render("overview.html", page_exam=page_exam, info_url=info_url, online_url=online_url)


@login_required
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
@referer_exam_no
def get_exam_info():
    find_type = re.findall("exam_type=(\\w+)", g.ref_url)
    if len(find_type) > 0:
        exam_type = find_type[0]
    elif "exam_type" in request.args:
        exam_type = request.args["exam_type"]
    else:
        exam_type = None
    items = c_exam.select_exam(exam_type, g.exam_no)
    return jsonify({"status": True, "data": items})


@exam_view.route("/info/", methods=["PUT"])
def update_exam():
    data = g.request_data
    exam_no = data["exam_no"]
    l = c_exam.update_exam(data["exam_type"], exam_no, data["exam_name"], data["exam_desc"],
                           data["eval_type"], pic_url=data["pic_url"])
    cases = dict()
    for i in range(len(data["result_explain"])):
        cases["case_%s" % string.letters[i]] = data["result_explain"][i]
    l2 = c_exam.update_result_explain(exam_no, **cases)
    return jsonify({"status": True, "data": data})


@exam_view.route("/info/", methods=["DELETE"])
def delete_exam():
    exam_no = g.request_data["exam_no"]
    exam_type = g.request_data["exam_type"]
    l = c_exam.delete_exam(exam_type, exam_no)
    return jsonify({"status": True, "data": "删除成功"})


@exam_view.route("/questions/", methods=["POST", "PUT"])
@required_exam_no
def entry_questions():
    data = g.request_data
    question_no = data["question_no"]
    question_desc = data["question_desc"]
    select_mode = data["select_mode"]
    options = data["options"]
    if request.method == "POST":
        r, l = c_exam.new_exam_questions(g.exam_no, question_no, question_desc, select_mode, options)
    else:
        l = c_exam.update_exam_questions(g.exam_no, question_no, question_desc, select_mode, options)
        r = True
    return jsonify({"status": r, "data": dict(action=request.method, data=data)})


@exam_view.route("/questions/", methods=["GET"])
@required_exam_no
def get_exam_questions():
    items = c_exam.select_questions(g.exam_no)
    return jsonify({"status": True, "data": items})


@exam_view.route("/online/", methods=["POST"])
def online_exam():
    exam_no = g.request_data["exam_no"]
    exam_type = g.request_data["exam_type"]
    items = c_exam.select_exam(exam_type, exam_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "测试不存在"})
    if items[0]["status"] & 7 != 7:
        return jsonify({"status": False, "data": "测试状态未达到不可上线"})
    c_exam.online_exam(exam_no)
    return jsonify({"status": True, "data": "success"})


@exam_view.route("/records/", methods=["POST"])
def add_exam_records():
    data = g.request_data
    exam_type = data["exam_type"]
    exam_no = data["exam_no"]
    user_id = data["user_id"]
    result = data["result"]
    c_exam.new_exam_record(user_id, exam_no, result)
    explains = c_exam.select_result_explain(exam_no, result)
    tj = c_exam.select_tj(exam_no)
    r = dict(result=result)
    if len(tj) > 0:
        r["tj"] = tj[0]
    else:
        r["tj"] = None
    if len(explains) > 0:
        r["result_explain"] = explains[0]
    else:
        r["result_explain"] = None
    return jsonify({"status": True, "data": r})

@exam_view.route("/explain/", methods=["GET"])
@required_exam_no
def get_explains():
    explains = c_exam.select_result_explain(g.exam_no)
    if len(explains) <= 0:
        return jsonify({"status": False, "data": "结果解释不存在"})
    if "list" not in request.args:
        return jsonify({"status": True, "data": explains[0]})
    explain_item = explains[0]
    keys = filter(lambda x: x.startswith("case_"), explain_item.keys())
    keys.sort()
    l_explains = []
    for key in keys:
        if explain_item[key] is None:
            break
        else:
            l_explains.append(explain_item[key])
    return jsonify({"status": True, "data": l_explains})

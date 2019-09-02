# !/usr/bin/env python
# coding: utf-8
import os
import re
import string
from functools import wraps
from flask import request, jsonify, g
from flask_login import login_required
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, upload_folder, file_prefix_url
from classes.exam import Exam
from web02 import create_blue

__author__ = 'meisa'

url_prefix = "/exam"

rt = RenderTemplate("exam", menu_active="exam")
menu_list = {"title": u"试题库", "icon_class": "icon-exam", "menu_id": "exam", "sub_menu": [
    {"title": u"试题库管理", "url": url_prefix + "/"},
    {"title": u"添加试题库", "url": url_prefix + "/?action=exam"},
    {"title": u"试题管理", "url": url_prefix + "/question/"},
    {"title": u"试题搜索", "url": url_prefix + "/search/"}
]}

exam_view = create_blue("exam", url_prefix=url_prefix, auth_required=False, menu_list=menu_list)
c_exam = Exam(db_conf_path)

G_SELECT_MODE = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题"]
G_SUBJECT = ["无", "微观经济学", "宏观经济学", "政治经济学"]


def separate_image(text):
    text_groups = []
    s_l = re.findall(r"(\[\[([/\w.]+?):([\d.]+?):([\d.]+?)\]\])", text)
    last_point = 0
    for items in s_l:
        item = items[0]
        point = text[last_point:].index(item)
        prefix_s = text[last_point: last_point + point]
        if len(prefix_s) > 0:
            text_groups.append(prefix_s)
        o_item = dict(url=items[1], width=float(items[2]), height=float(items[3]))
        text_groups.append(o_item)
        last_point = last_point + point + len(item)
    if last_point < len(text):
        text_groups.append(text[last_point:])
    return text_groups


def referer_exam_no(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Referer" not in request.headers:
            g.ref_url = ""
            g.exam_no = None
        else:
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


@exam_view.route("/", methods=["GET"])
@login_required
def index():
    add_url = url_prefix + "/"
    url_upload = url_prefix + "/upload/"
    info_url = url_prefix + "/info/"
    online_url = url_prefix + "/online/"
    explain_url = url_prefix + "/explain/"
    questions_url = url_prefix + "/questions/"
    page_exam = url_prefix + "/?action=exam"
    page_list = url_prefix + "/"
    if "action" in request.args and request.args["action"] == "exam":
        if "exam_no" in request.args:
            return rt.render("update_info.html", page_list=page_list, page_exam=page_exam, info_url=info_url,
                             upload_url=url_upload, explain_url=explain_url)
        return rt.render("entry_info.html", add_url=add_url, upload_url=url_upload, page_title=u"新建题库")
    if "exam_no" in request.args:
        return rt.render("entry_questions.html", page_list=page_list, page_exam=page_exam, info_url=info_url,
                         questions_url=questions_url, page_title=u"试题管理", url_upload=url_upload)
    return rt.render("overview.html", info_url=info_url, online_url=online_url, page_title=u"试题库")


@exam_view.route("/question/", methods=["GET"])
@login_required
def question_page():
    info_url = url_prefix + "/info/"
    questions_url = url_prefix + "/questions/"
    url_upload = url_prefix + "/upload/"
    return rt.render("entry_questions.html", info_url=info_url, questions_url=questions_url, page_title=u"试题管理",
                     url_upload=url_upload)


@exam_view.route("/", methods=["POST"])
@login_required
def new_exam():
    data = g.request_data
    r, exam_no = c_exam.new_exam(data["exam_name"], data["exam_type"], data["exam_desc"], 0, g.user_no)
    if r is False:
        return jsonify({"status": False, "data": "请重试"})
    data["exam_no"] = exam_no
    return jsonify({"status": True, "data": data})


support_upload2(exam_view, upload_folder, file_prefix_url, ("exam", "pic"), "upload", rename_mode="sha1")


@exam_view.route("/info/", methods=["GET"])
@login_required
@referer_exam_no
def get_exam_info():
    find_type = re.findall("exam_type=(\\w+)", g.ref_url)
    if len(find_type) > 0:
        exam_type = find_type[0]
    elif "exam_type" in request.args:
        exam_type = request.args["exam_type"]
    else:
        exam_type = None
    items = c_exam.select_exam(g.exam_no)
    for item in items:
        item["select_modes"] = G_SELECT_MODE
        item["subjects"] = G_SUBJECT
    if g.user_no is None:
        for i in range(len(items) - 1, -1, -1):
            if items[i]["status"] & 64 == 64:
                continue
            del items[i]
    return jsonify({"status": True, "data": items})


@exam_view.route("/info/", methods=["PUT"])
@login_required
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
@login_required
def delete_exam():
    exam_no = g.request_data["exam_no"]
    exam_type = g.request_data["exam_type"]
    l = c_exam.delete_exam(exam_type, exam_no)
    return jsonify({"status": True, "data": "删除成功"})


@exam_view.route("/questions/", methods=["POST", "PUT"])
@login_required
@required_exam_no
def entry_questions():
    data = g.request_data
    extra_data = dict()
    question_no = data["question_no"]
    question_desc = data["question_desc"]
    select_mode = data["select_mode"]
    question_subject = data["question_subject"]
    question_source = data["question_source"]
    if question_source and question_source.strip():
        extra_data["question_source"] = question_source.strip()
    if question_subject:
        extra_data["question_subject"] = question_subject
    options = data["options"]
    answer = data["answer"]
    if "question_desc_url" in data:
        extra_data["question_desc_url"] = data["question_desc_url"]

    if request.method == "POST":
        r, l = c_exam.new_exam_questions(g.exam_no, question_no,
                                         question_desc, select_mode,
                                         options, answer, **extra_data)
    else:
        l = c_exam.update_exam_questions(g.exam_no, question_no,
                                         question_desc, select_mode,
                                         options, answer, **extra_data)
        r = True
    return jsonify({"status": r, "data": dict(action=request.method, data=data)})


@exam_view.route("/questions/", methods=["GET"])
@login_required
@required_exam_no
def get_exam_questions():
    nos = request.args.get("nos", None)
    num = request.args.get("num", None)
    start_no = int(request.args.get("start_no", -1))
    if nos is not None:
        q_nos = filter(lambda x: len(x) > 0, re.split("\D", nos))
        items = c_exam.select_multi_question(g.exam_no, q_nos)
    elif num is None:
        # 获取全部试题
        items = c_exam.select_questions(g.exam_no)
    elif start_no == -1:
        # 获得随机试题num个
        items = c_exam.select_random_questions(g.exam_no, int(num))
    else:
        # 获得从start_no 获取试题num个
        desc = False
        if "desc" in request.args and request.args["desc"] == "true":
            desc = True
        items = c_exam.select_questions(g.exam_no, start_no=start_no, num=int(num), desc=desc)
    for item in items:
        question_desc_rich = separate_image(item["question_desc"])
        item["question_desc_rich"] = question_desc_rich
        for option in item["options"]:
            option["desc_rich"] = separate_image(option["desc"])
        item["answer_rich"] = separate_image(item["answer"])

    if g.user_no is None:
        for item in items:
            options = item["options"]
            new_options = map(lambda x: x["desc"], options)
            item["options"] = new_options
    return jsonify({"status": True, "data": items})


@exam_view.route("/questions/no/", methods=["GET"])
@required_exam_no
def get_max_exam_questions():
    max_no = c_exam.select_max_question(g.exam_no)
    next_no = (max_no + 1) if isinstance(max_no, (int, long)) else 1
    return jsonify({"status": True, "data": dict(max_no=max_no, next_no=next_no)})


@exam_view.route("/online/", methods=["POST"])
@login_required
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


@exam_view.route("/wrong/", methods=["POST"])
@login_required
def wrong_answer_action():
    exam_no = g.request_data["exam_no"]
    question_no = g.request_data["question_no"]
    c_exam.new_exam_wrong(g.user_no, exam_no, question_no)
    return jsonify({"status": True, "data": "success"})


@exam_view.route("/wrong/", methods=["GET"])
@login_required
@required_exam_no
def my_wrong_action():
    items = c_exam.select_wrong(g.user_no, g.exam_no)
    return jsonify({"status": True, "data": items})


@exam_view.route("/wrong/", methods=["DELETE"])
@login_required
@required_exam_no
def remove_my_wrong_action():
    question_no = g.request_data["question_no"]
    l = c_exam.delete_wrong(g.user_no, g.exam_no, question_no)
    d_item = dict(exam_no=g.exam_no, question_no=question_no, l=l)
    return jsonify({"status": True, "data": d_item})


@exam_view.route("/search/", methods=["GET"])
@login_required
def search_question_page():
    return rt.render("search.html", page_title=u"试题搜索")
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


def separate_image(text, max_width=None):
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
        if max_width and max_width < o_item["width"]:
            o_item["height"] = o_item["height"] * max_width / o_item["width"]
            o_item["width"] = max_width
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
        if g.exam_no:
            # 判定用户 对exam_no的权限
            # 判断session中是否有权限信息
            # 判断session中的信息是否过期
            # 重新获取权限信息
            pass
        return f(*args, **kwargs)
    return decorated_function


def required_exam_no(f):
    @wraps(f)
    @referer_exam_no
    def decorated_function(*args, **kwargs):
        if g.exam_no is None:
            return jsonify({"status": False, "data": "Bad Request"})
        if(g.user_role & 2) == 2:
            g.exam_role = 0
        else:
            exist_items = c_exam.select_exam(g.exam_no)
            if len(exist_items) <= 0:
                return jsonify({"status": False, "data": "Bad Request. "
                                                         "Exam no exist"})
            exam_item = exist_items[0]
            if int(exam_item['adder']) == g.user_no:
                g.exam_role = 1
            else:
                e_items = c_exam.user_exams(g.user_no, g.exam_no)
                if len(e_items) <= 0:
                    if exam_item["status"] & 64 == 64:
                        g.exam_role = 10
                    else:
                        return jsonify({"status": False, "data": "Bad "
                                                                 "Request"})
                else:
                    g.exam_role = e_items[0]['exam_role']
        return f(*args, **kwargs)
    return decorated_function


def required_manager_exam(key, **role_desc):
    min_role = role_desc.pop('min_role', 0)
    max_role = role_desc.pop('max_role', 3)

    def _decorated_function(func):
        @wraps(func)
        def _func(*args, **kwargs):
            data = request.json
            if key not in data:
                return jsonify({'status': False, 'data': 'need key %s' % key})
            exam_no = data[key]
            if (g.user_role & 2) == 2:
                exam_role = 0
            else:
                exist_items = c_exam.select_exam(exam_no)
                if len(exist_items) <= 0:
                    return jsonify({"status": False, "data": 'exam %s not '
                                                             'exist' % exam_no})
                if int(exist_items[0]['adder']) == g.user_no:
                    exam_role = 1
                else:
                    e_items = c_exam.user_exams(g.user_no, exam_no)
                    if len(e_items) <= 0:
                        exam_role = 10
                    else:
                        exam_role = e_items[0]['exam_role']
            if exam_role < min_role or exam_role > max_role:
                return jsonify({"status": False, "data": 'forbidden'})
            setattr(g, key, exam_no)
            return func(*args, **kwargs)
        return _func
    return _decorated_function


@exam_view.route("/", methods=["GET"])
@login_required
def index():
    add_url = url_prefix + "/"
    url_upload = url_prefix + "/upload/"
    info_url = url_prefix + "/info/"
    online_url = url_prefix + "/online/"
    questions_url = url_prefix + "/questions/"
    page_exam = url_prefix + "/?action=exam"
    page_list = url_prefix + "/"
    if "action" in request.args and request.args["action"] == "exam":
        if "exam_no" in request.args:
            return rt.render("entry_info.html", page_list=page_list, page_exam=page_exam, info_url=info_url,
                             upload_url=url_upload)
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
    r, exam_no = c_exam.new_exam(data["exam_name"], data["exam_desc"], g.user_no)
    if r is False:
        return jsonify({"status": False, "data": "请重试"})
    data["exam_no"] = exam_no
    return jsonify({"status": True, "data": data})


support_upload2(exam_view, upload_folder, file_prefix_url, ("exam", "pic"), "upload", rename_mode="sha1")


@exam_view.route("/info/", methods=["GET"])
@login_required
@referer_exam_no
def get_exam_info():
    min_role = 10
    if 'is_admin' in request.args:
        min_role = 3
    items = c_exam.select_exam(g.exam_no)
    u_exams = c_exam.select_user_exams(g.user_no)
    for item in items:
        item["select_modes"] = G_SELECT_MODE
        item["subjects"] = G_SUBJECT
    for i in range(len(items) - 1, -1, -1):
        exam_no = items[i]['exam_no']
        if int(items[i]["adder"]) == g.user_no:
            items[i]['exam_role'] = 1
        elif exam_no in u_exams:
            items[i].update(u_exams[exam_no])
        elif (g.user_role & 2) == 2:
            items[i]['exam_role'] = 0  # 内部用户全部返回
        elif items[i]["status"] & 64 == 64:
            items[i]['exam_role'] = 10
        else:
            items[i]['exam_role'] = 100
        if items[i]['exam_role'] > min_role:
            del items[i]
    return jsonify({"status": True, "data": items})


@exam_view.route("/info/", methods=["PUT"])
@login_required
def update_exam():
    data = g.request_data
    exam_no = data["exam_no"]
    l = c_exam.update_exam(exam_no, data["exam_name"], data["exam_desc"],
                           pic_url=data["pic_url"])
    return jsonify({"status": True, "data": data})


@exam_view.route("/info/", methods=["DELETE"])
@login_required
def delete_exam():
    exam_no = g.request_data["exam_no"]
    exam_type = g.request_data["exam_type"]
    l = c_exam.delete_exam(exam_type, exam_no)
    return jsonify({"status": True, "data": "删除成功"})


@exam_view.route("/questions/", methods=["POST"])
@login_required
@required_exam_no
def entry_questions():
    if g.exam_role > 3:
        return jsonify({'status': False, 'data': 'forbidden'})
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
    if "inside_mark" in data:
        extra_data["inside_mark"] = data["inside_mark"]

    r, l = c_exam.new_exam_questions(g.exam_no, question_no, question_desc,
                                     select_mode, options, answer,
                                     **extra_data)

    return jsonify({"status": r, "data": dict(action=request.method, data=data)})


@exam_view.route("/questions/", methods=["PUT"])
@login_required
@required_exam_no
def update_question():
    if g.exam_role > 3:
        return jsonify({'status': False, 'data': 'forbidden'})
    data = g.request_data
    extra_data = dict()
    question_no = data["question_no"]
    keys = ("question_desc", "select_mode", "question_subject",
            "question_source", "options", "answer", "question_desc_url")
    for key in keys:
        if key in data:
            extra_data[key] = data[key]
    l = c_exam.update_exam_questions(g.exam_no, question_no, **extra_data)
    return jsonify({"status": True, "data": dict(action=request.method, data=data)})


@exam_view.route("/questions/", methods=["GET"])
@login_required
@required_exam_no
def get_exam_questions():
    nos = request.args.get("nos", None)
    num = request.args.get("num", None)
    start_no = int(request.args.get("start_no", -1))
    select_mode = request.args.get("select_mode", None)
    question_subject = request.args.get("question_subject", None)
    no_rich = request.args.get("no_rich", False)
    if nos is not None:
        q_nos = filter(lambda x: len(x) > 0, re.split("\D", nos))
        items = c_exam.select_multi_question(g.exam_no, q_nos)
    elif num is None:
        # 获取全部试题
        items = c_exam.select_questions(g.exam_no)
    elif start_no == -1:
        # 获得随机试题num个
        items = c_exam.select_random_questions(g.exam_no, int(num), select_mode, question_subject)
    else:
        # 获得从start_no 获取试题num个
        desc = False
        if "desc" in request.args and request.args["desc"] == "true":
            desc = True
        items = c_exam.select_questions(g.exam_no, start_no=start_no, num=int(num), desc=desc)

    if g.user_no is None:
        for item in items:
            options = item["options"]
            new_options = map(lambda x: x["desc"], options)
            item["options"] = new_options

    if no_rich is False:
        max_width = None
        if "X-Device-Screen-Width" in request.headers:
            max_width = int(request.headers["X-Device-Screen-Width"]) * 0.95
        for item in items:
            question_desc_rich = separate_image(item["question_desc"])
            item["question_desc_rich"] = question_desc_rich
            for option in item["options"]:
                option["desc_rich"] = separate_image(option["desc"])
            item["answer_rich"] = separate_image(item["answer"], max_width)

    return jsonify({"status": True, "data": items})


@exam_view.route("/questions/no/", methods=["GET"])
@required_exam_no
def get_exam_questions_nos():
    if "select_mode" in request.args:
        select_mode = request.args["select_mode"]
        question_subject = request.args.get("question_subject", None)
        items = c_exam.select_question_no(g.exam_no, select_mode=select_mode,
                                          question_subject=question_subject)
        nos = map(lambda x: x["question_no"], items)
        return jsonify({"status": True, "data": dict(exam_no=g.exam_no, questions=items)})
    max_no = c_exam.select_max_question(g.exam_no)
    next_no = (max_no + 1) if isinstance(max_no, (int, long)) else 1
    return jsonify({"status": True, "data": dict(max_no=max_no, next_no=next_no)})


@exam_view.route("/online/", methods=["POST"])
@login_required
def online_exam():
    exam_no = g.request_data["exam_no"]
    items = c_exam.select_exam(exam_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "测试不存在"})
    if items[0]["status"] & 3 != 3:
        return jsonify({"status": False, "data": "测试状态未达到不可上线"})
    c_exam.online_exam(exam_no)
    return jsonify({"status": True, "data": "success"})


@exam_view.route("/online/", methods=["DELETE"])
@login_required
def offline_exam():
    exam_no = g.request_data["exam_no"]
    exam_type = g.request_data["exam_type"]
    c_exam.offline_exam(exam_no)
    return jsonify({"status": True, "data": "success"})


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
    min_wrong_time = int(request.args.get("min_wrong_time", 0))
    items = c_exam.select_wrong(g.user_no, g.exam_no, min_wrong_time)
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


@exam_view.route('/member', methods=['POST'])
@login_required
def new_member():
    data = request.json
    exam_no = data['exam_no']
    allow_update = data.get('allow_update', False)
    end_time = data.get('end_time', None)
    if (g.user_role & 2) != 2:
        exist_items = c_exam.select_exam(exam_no)
        if len(exist_items) <= 0:
            return jsonify({"status": False, "data": 'forbidden'})
        if int(exist_items[0]['adder']) != g.user_no:
            e_items = c_exam.user_exams(g.user_no, exam_no)
            if len(e_items) <= 0:
                return jsonify({"status": False, "data": 'forbidden'})
            if e_items[0]['exam_role'] > 2:
                return jsonify({"status": False, "data": 'forbidden'})
    member_no = data['member_no']
    items = c_exam.user_exams(member_no, exam_no)
    if len(items) > 0:
        if not allow_update:
            return jsonify({"status": False, "data": '已存在'})
        else:
            c_exam.update_exam_member(member_no, exam_no, g.user_no, end_time=end_time)
    else:
        c_exam.new_exam_member(member_no, exam_no, g.user_no, end_time=end_time)
    return jsonify({"status": True, "data": 'success'})


@exam_view.route('/member', methods=['GET'])
@login_required
@required_exam_no
def get_member():
    exam_no = g.exam_no
    if (g.user_role & 2) != 2:
        exist_items = c_exam.select_exam(exam_no)
        if len(exist_items) <= 0:
            return jsonify({"status": False, "data": 'forbidden'})
        if int(exist_items[0]['adder']) != g.user_no:
            e_items = c_exam.user_exams(g.user_no, exam_no)
            if len(e_items) <= 0:
                return jsonify({"status": False, "data": 'forbidden'})
            if e_items[0]['exam_role'] > 2:
                return jsonify({"status": False, "data": 'forbidden'})
    member_no = request.args['member_no']
    items = c_exam.user_exams(member_no, exam_no)
    if len(items) <= 0:
        return jsonify({"status": True, "data": None})
    return jsonify({"status": True, "data": items[0]})


@exam_view.route('/transfer', methods=['POST'])
@login_required
@required_manager_exam('source_exam_no')
@required_manager_exam('target_exam_no')
def transfer_exam():
    data = request.json
    source_exam_no = data['source_exam_no']
    start_no = data['start_no']
    end_no = data['end_no']
    target_exam_no = data['target_exam_no']
    items = c_exam.transfer_exam(source_exam_no, start_no, end_no,
                                 target_exam_no)
    return jsonify({'status': True, 'data': items})

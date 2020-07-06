# !/usr/bin/env python
# coding: utf-8
from collections import OrderedDict
import re
import time
from functools import wraps
from werkzeug.utils import secure_filename
import uuid

from flask import request, jsonify, g
from flask_login import login_required
from flask_helper.template import RenderTemplate
from flask_helper.upload import support_upload2

from zh_config import db_conf_path, upload_folder, file_prefix_url
from zh_config import min_program_conf, es_conf
from wildzh.classes.exam import Exam, ExamObject, StrategyObject
from wildzh.classes.exam_es import ExamEs
from wildzh.classes.user import User
from wildzh.classes.wx import MiniProgram
from wildzh.export.local_write import write_docx
from wildzh.tools.docx.object import DocxObject
from wildzh.tools.handle_exam import QuestionSet
from wildzh.tools.parse_exception import ParseException
from wildzh.tools.parse_question import AnswerLocation
from wildzh.tools.read_xml import handle_docx_main_xml
from wildzh.utils.async_pool import get_pool
from wildzh.utils.log import getLogger
from wildzh.web02.view import View2

__author__ = 'meisa'

LOG = getLogger()
url_prefix = "/exam"

add_url = url_prefix + "/"
upload_url = url_prefix + "/upload/"
info_url = url_prefix + "/info/"
online_url = url_prefix + "/online/"
questions_url = url_prefix + "/questions/"
page_exam = url_prefix + "/?action=exam"
page_question_url = url_prefix + '/question/'
strategy_url = url_prefix + '/strategy'
query_url = url_prefix + '/query'
file_url = url_prefix + '/question/file'
defined_routes = dict(add_url=add_url, upload_url=upload_url,
                      info_url=info_url, online_url=online_url,
                      questions_url=questions_url, page_exam=page_exam,
                      strategy_url=strategy_url, query_url=query_url,
                      page_question_url=page_question_url, file_url=file_url)
rt = RenderTemplate("exam", menu_active="exam", defined_routes=defined_routes)
menu_list = {"title": u"试题库", "icon_class": "icon-exam", "menu_id": "exam", "sub_menu": [
    {"title": u"试题库管理", "url": url_prefix + "/"},
    {"title": u"添加试题库", "url": url_prefix + "/?action=exam"},
    {"title": u"试题管理", "url": url_prefix + "/question/"},
    {"title": u"导入试题", "url": url_prefix + "/question/import"},
    {"title": u"组卷策略", "url": url_prefix + "/strategy"},
    {"title": u"试题搜索", "url": url_prefix + "/search/"}
]}

exam_view = View2("exam", __name__, url_prefix=url_prefix,
                  auth_required=False, menu_list=menu_list)

c_exam = Exam(db_conf_path)
c_user = User(db_conf_path=db_conf_path, upload_folder=upload_folder)
c_exam_es = ExamEs(es_conf)
min_pro = MiniProgram(conf_path=min_program_conf, section='01')
ASYNC_POOL = get_pool()

G_SELECT_MODE = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题"]


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
            return jsonify({"status": False, "data": "Bad Request. exam_no"
                                                     " not in request"})
        exist_items = c_exam.select_exam2(g.exam_no)
        if len(exist_items) <= 0:
            return jsonify({"status": False, "data": "Bad Request. "
                                                     "Exam no exist"})
        exam_item = exist_items[0]
        if(g.user_role & 2) == 2:
            g.exam_role = 0
        else:
            if int(exam_item.adder) == g.user_no:
                g.exam_role = 1
            else:
                e_items = c_exam.user_exams(g.user_no, g.exam_no)
                if len(e_items) <= 0:
                    g.exam_role = exam_item.exam_role
                    if g.exam_role == 100:
                        return jsonify({"status": False, "data": "Bad "
                                                                 "Request. Forbidden"})
                else:
                    g.exam_role = e_items[0]['exam_role']
        g.current_exam = exam_item
        return f(*args, **kwargs)
    return decorated_function


def required_manager_exam(key='exam_no', **role_desc):
    min_role = role_desc.pop('min_role', 0)
    max_role = role_desc.pop('max_role', 3)
    param_location = role_desc.pop('param_location', 'body')

    def _decorated_function(func):
        @wraps(func)
        def _func(*args, **kwargs):
            if param_location == 'args':
                data = request.args
            else:
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
    page_exam = url_prefix + "/?action=exam"
    page_list = url_prefix + "/"
    if "action" in request.args and request.args["action"] == "exam":
        if "exam_no" in request.args:
            return rt.render("entry_info.html", page_list=page_list, page_exam=page_exam,
                             page_title=u'更新题库')
        return rt.render("entry_info.html", page_title=u"新建题库")
    if "exam_no" in request.args:
        return rt.render("entry_questions.html", page_list=page_list,
                         page_exam=page_exam, page_title=u"试题管理")
    return rt.render("overview.html", page_title=u"试题库")


@exam_view.route("/question/", methods=["GET"])
@login_required
def question_page():
    return rt.render("entry_questions.html", page_title=u"试题管理")


@exam_view.route("/", methods=["POST"])
@login_required
def new_exam():
    data = g.request_data
    eo = ExamObject()
    for key in data.keys():
        setattr(eo, key, data[key])
    eo.adder = g.user_no
    r, exam_no = c_exam.new_exam(**eo.to_db_dict())
    if r is False:
        return jsonify({"status": False, "data": "请重试"})
    data["exam_no"] = exam_no
    return jsonify({"status": True, "data": data})


support_upload2(exam_view, upload_folder, file_prefix_url, ("exam", "pic"), "upload", rename_mode="sha1")


@exam_view.route("/info/", methods=["GET"])
@login_required
@referer_exam_no
def get_exam_info():
    min_role = 25
    if 'is_admin' in request.args:
        min_role = 3
    items = c_exam.select_exam2(g.exam_no)
    r_items = []
    u_exams = c_exam.select_user_exams(g.user_no)
    for i in range(len(items) - 1, -1, -1):
        item = items[i]
        r_item = item.to_dict()
        exam_no = item.exam_no
        if int(item.adder) == g.user_no:
            r_item['exam_role'] = 1
            r_item['end_time'] = None
        elif exam_no in u_exams:
            r_item.update(u_exams[exam_no])
        elif (g.user_role & 2) == 2:
            r_item['exam_role'] = 0  # 内部用户全部返回
            r_item['end_time'] = None
        else:
            r_item['exam_role'] = item.exam_role
        if 'end_time' not in r_item:
            r_item['end_time'] = 0
        if r_item['exam_role'] <= min_role:
            r_items.append(r_item)

    if 'rich' in request.args:
        for item in r_items:
            item['rich_exam_desc'] = separate_image(item['exam_desc'])
    return jsonify({"status": True, "data": r_items})


@exam_view.route("/info/", methods=["PUT"])
@login_required
def update_exam():
    data = g.request_data
    exam_no = data["exam_no"]
    items = c_exam.select_exam2(exam_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "Exam not exist"})
    for key in data.keys():
        setattr(items[0], key, data[key])

    l = c_exam.update_exam(**items[0].to_db_dict())
    return jsonify({"status": True, "data": data})


@exam_view.route("/info/", methods=["DELETE"])
@login_required
def delete_exam():
    exam_no = g.request_data["exam_no"]
    l = c_exam.delete_exam(exam_no)
    return jsonify({"status": True, "data": "删除成功"})


def sync_one_question(exam_no, q_item, update=False):
    doc_id = '%s_%s' % (exam_no, q_item['question_no'])
    if 'question_desc' not in q_item:
        _c_exam = Exam(db_conf_path)
        q_item = _c_exam.select_one_question(exam_no, q_item['question_no'])
    desc = q_item['question_desc']
    answer = q_item['answer']
    options = ''
    if q_item['select_mode'] == 0:
        options = '\n'.join([o['desc'] for o in q_item['options']])
    if update:
        c_exam_es.update_one_item(doc_id, desc, options, answer)
    else:
        c_exam_es.add_one_item(doc_id, desc, options, answer)


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
    select_mode = int(data["select_mode"])
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
    sync_one_question(g.exam_no, {'question_no': question_no}, update=False)
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
            "question_source", "options", "answer", "question_desc_url",
            'question_chapter', 'state')
    for key in keys:
        if key in data:
            extra_data[key] = data[key]
    l = c_exam.update_exam_questions(g.exam_no, question_no, **extra_data)
    sync_one_question(g.exam_no, {'question_no': question_no}, update=True)
    return jsonify({"status": True, "data": dict(action=request.method, data=data)})


def handle_questions(q_items, no_rich=False):
    if g.user_no is None:
        for item in q_items:
            options = item["options"]
            new_options = map(lambda x: {'desc': x["desc"]}, options)
            item["options"] = new_options
    # 按照用户对 题库的权限 再处理 题目
    exam_item = g.current_exam
    if g.exam_role > 10:
        for item in q_items:
            if not exam_item.verify_no(item['question_no']):
                item['question_desc'] = '请升级为会员！'
                item['options'] = []
                item['answer'] = '请升级为会员！'
            else:
                if not exam_item.can_look_analysis():
                    item['answer'] = '请升级为会员！'
                if not exam_item.can_look_answer():
                    options = item['options']
                    item['options'] = map(lambda x: {'desc': x["desc"]}, options)
                if not exam_item.can_look_subject():
                    item['question_desc'] = '请升级为会员！'
                    item['options'] = []

    if no_rich is False:
        max_width = None
        if "X-Device-Screen-Width" in request.headers:
            max_width = int(request.headers["X-Device-Screen-Width"]) * 0.95
        for item in q_items:
            question_desc_rich = separate_image(item["question_desc"],
                                                max_width)
            del item['question_desc']
            item["question_desc_rich"] = question_desc_rich
            for option in item["options"]:
                option["desc_rich"] = separate_image(option["desc"])
                del option["desc"]
            item["answer_rich"] = separate_image(item["answer"], max_width)
            del item['answer']
    return q_items


@exam_view.route("/questions/", methods=["GET"])
@login_required
@required_exam_no
def get_exam_questions():
    start_time = time.time()
    nos = request.args.get("nos", None)
    strategy_id = request.args.get('strategy_id', None)
    num = request.args.get("num", None)
    start_no = int(request.args.get("start_no", -1))
    select_mode = int(request.args.get("select_mode", -1))
    question_subject = request.args.get("question_subject", None)
    no_rich = request.args.get("no_rich", False)
    exclude_nos = request.args.get("exclude_nos", "")
    if nos is not None:
        q_nos = list(filter(lambda x: len(x) > 0, re.split("\D", nos)))
        items = c_exam.select_multi_question2(g.exam_no, q_nos)
    elif strategy_id:
        # 按照策略获得试题
        items = c_exam.get_questions_by_strategy(g.exam_no, strategy_id,
                                                 question_subject)
    elif num is None:
        # 获取全部试题
        items = c_exam.select_questions(g.exam_no)
    elif start_no == -1:
        # 获得随机试题num个
        items = c_exam.select_random_questions(g.exam_no, int(num),
                                               select_mode,
                                               question_subject,
                                               exclude_nos)
    else:
        # 获得从start_no 获取试题num个
        desc = False
        if "desc" in request.args and request.args["desc"] == "true":
            desc = True
        items = c_exam.select_questions(g.exam_no, start_no=start_no, num=int(num), desc=desc)

    items = handle_questions(items, no_rich)
    use_time = time.time() - start_time
    exam_item = g.current_exam.to_dict()
    exam_item['exam_role'] = g.exam_role
    return jsonify({"status": True, "data": items, 'use_time': use_time,
                    'exam': exam_item})


@exam_view.route("/questions/no/", methods=["GET"])
@login_required
@required_exam_no
def get_exam_questions_nos():
    if "select_mode" in request.args:
        select_mode = int(request.args["select_mode"])
        question_subject = request.args.get("question_subject", None)
        question_chapter = request.args.get('question_chapter', None)
        question_source = request.args.get('question_source', None)
        start_no = request.args.get('start_no', None)
        items = c_exam.select_question_no(g.exam_no, select_mode=select_mode,
                                          question_subject=question_subject,
                                          start_no=start_no,
                                          question_chapter=question_chapter,
                                          question_source=question_source)

        if 'compress' in request.args:
            nos_l = []
            _start = 0
            _offset = 0
            for item in items:
                if item['question_no'] == _start + _offset:
                    _offset += 1
                else:
                    nos_l.append([_start, _offset])
                    _start = item['question_no']
                    _offset = 1
            if _start != 0:
                nos_l.append([_start, _offset])
            return jsonify({"status": True, "data": dict(exam_no=g.exam_no, nos=nos_l)})
        return jsonify({"status": True, "data": dict(exam_no=g.exam_no, questions=items)})
    max_no = c_exam.select_max_question(g.exam_no)
    next_no = (max_no + 1) if isinstance(max_no, (int, )) else 1
    return jsonify({"status": True, "data": dict(max_no=max_no, next_no=next_no)})


@exam_view.route("/questions/sources", methods=["GET"])
@login_required
@required_exam_no
def get_exam_sources():
    items = c_exam.get_sources(g.exam_no)
    data = {'exam_no': g.exam_no, 'sources': items}
    return jsonify({"status": True, "data": data})


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


@exam_view.route("/question/import/", methods=["GET"])
@login_required
def upload_question_page():
    return rt.render("question_import.html", page_title=u"试题上传")


@exam_view.route("/question/file/", methods=["POST"])
@login_required
def upload_question_file():
    r = dict()
    for key in request.files:
        file_item = request.files[key]
        filename = secure_filename(file_item.filename)
        extension = filename.rsplit(".", 1)[-1].lower()
        save_name = uuid.uuid4().hex + ".%s" % extension
        file_item.save(save_name)
        r[key] = save_name
    docx_path = r['q_file']
    s_kwargs = dict(dry_run=True, set_mode=False,
                    answer_location=AnswerLocation.embedded())
    q_set = QuestionSet(**s_kwargs)

    with DocxObject(docx_path) as do:
        try:
            handle_docx_main_xml(do, ".", u"、", u"．", ':',
                                 questions_set=q_set)
        except ParseException as pe:
            pass
        q_list = []
        for q_item in q_set:
            q_list.append(q_item.to_dict())
        data = {'q_list': q_list}
        return jsonify({"status": True, "data": data})


@exam_view.route("/strategy", methods=["GET"])
@login_required
def strategy_page():
    return rt.render("strategy.html", page_title=u"智能组卷策略")


@exam_view.route("/search/", methods=["GET"])
@login_required
def search_question_page():
    return rt.render("search.html", page_title=u"试题搜索")


@exam_view.route("/query", methods=["POST"])
@login_required
def query_question_items():
    data = request.json
    exam_no = data['exam_no']
    query_str = data['query_str']
    items = c_exam.query_questions(exam_no, query_str)
    query2_question_items()
    return {'status': True, 'data': items}


@exam_view.route("/query2", methods=["POST"])
@login_required
def query2_question_items():
    data = request.json
    exam_no = data['exam_no']
    query_str = data['query_str']
    item = c_exam.get_one_usage_records(g.user_no, g.exam_no)
    if item['num'] < 100:
        data = {'current': [], 'better_exams': []}
        data['message'] = '当前做题较少，暂无法使用！'
        return {'status': True, 'data': data}
    s_items = c_exam_es.search_multi(query_str)
    current = []
    c_score = -1
    others = OrderedDict()
    for item in  s_items:
        _id = item['_id']
        id_items = _id.split('_')
        if len(id_items) != 2:
            continue
        try:
            _exam_no, question_no = [int(i) for i in id_items]
        except ValueError:
            continue
        if _exam_no == exam_no:
            q_item = {'exam_no': _exam_no, 'question_no': question_no,
                      'question_desc': item['desc'],
                      'options': item['options'],
                      'answer': item['answer'],
                      'score': item['score']}
            if item['score'] > c_score:
                c_score = item['score']
            current.append(q_item)
            continue
        if _exam_no not in others:
            others[_exam_no] = {'score': -1, 'num': 0}
        others[_exam_no]['num'] += 1
        if item['score'] > others[_exam_no]['score']:
            others[_exam_no]['score'] = item['score']
    better_exams = []
    for o_exam_no, m_data in others.items():
        if m_data['score'] <= c_score:
            continue
        e_item , e_role = c_exam.user_exam_role(g.user_role, g.user_role,
                                                o_exam_no)
        if e_item is None:
            continue
        e_item_d = e_item.to_dict()
        e_item_d['exam_role'] = e_role
        e_item_d['match_num'] = m_data['num']
        better_exams.append(e_item_d)
    data = {'current': current, 'better_exams': better_exams}
    data['message'] = '功能测试中'
    return {'status': True, 'data': data}


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
    if g.exam_role > 2:
        return jsonify({"status": False, "data": 'forbidden'})
    member_no = request.args.get('member_no', None)
    if member_no:
        items = c_exam.user_exams(int(member_no), exam_no)
        if len(items) <= 0:
            item = None
        else:
            item = items[0]
        if 'flows' in request.args:
            flows = c_exam.select_member_flows(member_no, exam_no)
            flows.sort(key=lambda x: x['update_time'], reverse=True)
            data = {'current': item, 'flows': flows}
            return jsonify({"status": True, "data": data})
        return jsonify({"status": True, "data": item})
    else:
        items = c_exam.exam_members(exam_no)
    return jsonify({"status": True, "data": items})


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
    t_kwargs = dict()
    if 'target_start_no' in data:
        t_kwargs['target_start_no'] = data['target_start_no']
    if 'target_end_no' in data:
        t_kwargs['target_end_no'] = data['target_end_no']
    if 'select_mode' in data:
        t_kwargs['select_mode'] = data['select_mode']
    if 'random' in data and data['random']:
        t_kwargs['random'] = True
    r, items = c_exam.transfer_exam(source_exam_no, start_no, end_no,
                                    target_exam_no, **t_kwargs)
    ASYNC_POOL(start_sync_es, target_exam_no)
    return jsonify({'status': r, 'data': items})


@exam_view.route('/usage/state', methods=['GET'])
@login_required
@required_manager_exam(param_location='args')
def get_usage_state():
    period_no = request.args.get('period_no', None)
    offset_num = int(request.args.get('offset_num', 1))
    items = c_exam.get_usage_records(g.exam_no, period_no=period_no,
                                     offset_num=offset_num)
    return jsonify({'status': True, 'data': items})


@exam_view.route('/usage', methods=['GET'])
@login_required
@required_exam_no
def query_usage():
    item = c_exam.get_one_usage_records(g.user_no, g.exam_no)
    if(g.user_role & 2) != 2 and item['num'] < 100:
        item['num'] = -1
    return jsonify({'status': True, 'data': item})


@exam_view.route('/usage', methods=['POST'])
@login_required
@required_exam_no
def update_usage():
    data = request.json
    num = data['num']
    item = c_exam.update_usage_records(g.exam_no, g.user_no, num)
    return jsonify({'status': True, 'data': item})


@exam_view.route('/strategy/<int:exam_no>', methods=['GET'])
@login_required
def get_exam_strategy(exam_no):
    items = c_exam.get_strategy(exam_no=exam_no)
    data = {'exam_no': exam_no, 'strategies': items}
    return jsonify({'status': True, 'data': data})


@exam_view.route('/strategy', methods=['PUT', 'POST'])
@login_required
@required_manager_exam()
def set_exam_strategy():
    data = request.json
    strategy_o = StrategyObject.parse(**data)
    if not strategy_o:
        return jsonify({'status': False, 'data': ''})
    if strategy_o.id:
        c_exam.update_strategy(g.exam_no, **strategy_o.to_dict())
    else:
        c_exam.new_strategy(g.exam_no, **strategy_o.to_dict())
    return jsonify({'status': True, 'data': ''})


@exam_view.route('/strategy/<strategy_id>', methods=['DELETE'])
@login_required
@required_manager_exam()
def delete_exam_strategy(strategy_id):
    l = c_exam.delete_strategy(g.exam_no, strategy_id)
    return jsonify({'status': True, 'data': ''})


@exam_view.route('/export/word', methods=['POST', 'GET'])
@login_required
@required_exam_no
def export_question_to_word():
    # http://127.0.0.1:2400/exam/export/word?exam_no=1585396371&strategy_id=a1af47f5ec3d4829b143ec348c5f3479
    data = request.json or request.args
    strategy_id = data['strategy_id']
    strategies = c_exam.get_strategy(exam_no=g.exam_no,
                                     strategy_id=strategy_id)
    if len(strategies) != 1:
        return {'status': False, 'data': 'Not Found'}
    items = c_exam.get_questions_by_strategy(g.exam_no, strategy_id)
    items = handle_questions(items, False)
    write_docx('Test', False, items, G_SELECT_MODE, upload_folder)
    return {'status': True, 'data': strategies[0]}


@exam_view.route('/question/feedback', methods=['GET'])
@login_required
@required_exam_no
def get_question_feedback():
    args = request.args
    user_no = g.user_no
    if g.exam_role <= 3:
        user_no = None
    question_no = args.get('question_no', None)
    state = args.get('state', None)
    items = c_exam.get_question_feedback(g.exam_no, user_no, question_no, state)
    return {'status': True, 'data': items}


def notify_feedback(data):
    exam_no = data['exam_no']
    # 获得题库名称
    e_items = c_exam.select_exam(exam_no)
    if len(e_items) <= 0:
        return
    e_item = e_items[0]
    exam_name = e_item['exam_name']
    # 查询管理员
    admin_members = c_exam.exam_admin_members(exam_no)
    admin_nos = [u["user_no"] for u in admin_members]
    wx_ids = []
    for user_no in admin_nos:
        user_items = c_user.verify_user_exist(user_no=user_no)
        for u_item in user_items:
            if u_item['wx_id']:
                wx_ids.append(u_item['wx_id'])
    if len(data['description']) <= 0:
        data['description'] = '<用户未填写>'
    for wx_id in wx_ids:
        res = min_pro.send_fb_message(wx_id, exam_no, exam_name,
                                      data['fb_type'],
                                      data['question_no'],
                                      data['description'])
        print(res)
    return True


@exam_view.route('/question/feedback', methods=['POST'])
@login_required
@required_exam_no
def new_question_feedback():
    data = request.json
    user_no = g.user_no
    question_no = data['question_no']
    fb_type = data['fb_type']
    description = data['description']
    items = c_exam.new_question_feedback(g.exam_no, user_no, question_no,
                                         fb_type, description)
    n_data = data
    n_data['user_no'] = user_no
    n_data['exam_no'] = g.exam_no
    ASYNC_POOL.submit(notify_feedback, data)
    return {'status': True, 'data': 'success'}


@exam_view.route('/question/feedback', methods=['PUT'])
@login_required
@required_manager_exam()
def handle_question_feedback():
    data = request.json
    user_no = data['user_no']
    question_no = data['question_no']
    result = data['result']
    state = data['state']
    items = c_exam.update_question_feedback(g.exam_no, user_no, question_no,
                                            result=result, state=state)
    return {'status': True, 'data': 'success'}


def start_sync_es(exam_no, start_no=None, force=False):
    # 获得所有question_no
    LOG.info('start sync es %s start_no=%s force=%s', exam_no,
             start_no, force)
    _c_exam = Exam(db_conf_path)
    q_items = _c_exam.select_question_no(exam_no, start_no=start_no)
    LOG.info('query %s questions from %s', len(q_items), exam_no)
    missing_nos = []
    # 查看哪些没有数据
    for item in q_items:
        doc_id = '%s_%s' % (exam_no, item['question_no'])
        if force or not c_exam_es.exists(doc_id):
            missing_nos.append(item['question_no'])
    LOG.info('found missing_nos %s',  missing_nos)
    # 插入数据
    step = 30
    for i in range(0, len(missing_nos), step):
        try:
            a_items = _c_exam.select_multi_question2(exam_no,
                                                     missing_nos[i:i + step])
            for q_item in a_items:
                sync_one_question(exam_no, q_item, update=force)
        except Exception as e:
            LOG.error(e)
    LOG.info('success async es %s', exam_no)
    return missing_nos


@exam_view.route('/es/sync', methods=['POST', 'GET'])
@login_required
@required_manager_exam(param_location='args')
def sync_to_es():
    LOG.info('receive request sync %s', g.exam_no)
    if 'start_no' in request.args:
        start_no = int(request.args['start_no'])
        LOG.info('receive request sync %s start_no is %s', g.exam_no,
                 start_no)
        ASYNC_POOL(start_sync_es, g.exam_no, start_no=start_no, force=True)
    else:
        ASYNC_POOL.submit(start_sync_es, g.exam_no)
    return jsonify({'status': True, 'data': 'success'})


@exam_view.route('/es/one', methods=['POST', 'GET'])
@login_required
@required_manager_exam(param_location='args')
def get_one_from_es():
    exam_no = g.exam_no
    question_no = request.args['question_no']
    doc_id = '%s_%s' % (exam_no, question_no)
    r = c_exam_es.get_one(doc_id)
    return jsonify({'status': True, 'data': r})

# !/usr/bin/env python
# coding: utf-8
from flask import g, jsonify, session, request, redirect, make_response, send_from_directory
from flask_login import UserMixin, login_user, current_user, logout_user, login_required
from flask_helper.template import RenderTemplate

from zh_config import db_conf_path, web_pro, min_program_conf, upload_folder
from wildzh.classes.user import User
from wildzh.classes.wx import MiniProgram
from wildzh.web02 import login_manager
from wildzh.web02.view import View2
from wildzh.utils.log import getLogger

__author__ = 'meisa'

LOG = getLogger()
url_prefix = "/user"
rt = RenderTemplate("user")
c_user = User(db_conf_path=db_conf_path, upload_folder=upload_folder)
mp = MiniProgram(conf_path=min_program_conf, section=web_pro)
menu_list = [
    {"menu_id": "user", "index": -2, "url": "/password/", "title": u"个人中心", "icon_class": "icon-personal2"},
    {"menu_id": "exit", "index": -1, "url": "/login/", "title": u"退出", "icon_class": "icon-exit"}]
user_view = View2("user", __name__, url_prefix=url_prefix, auth_required=False,
                        menu_list=menu_list)
user_view.add_handler(c_user)


class FlaskUser(UserMixin):
    user_no = ""

    def get_id(self):
        return self.user_no


@login_manager.user_loader
def load_user(user_id):
    user = FlaskUser()
    user.user_no = user_id
    if "role" in session:
        user.role = session["role"]
    else:
        user.role = 0
        session["role"] = user.role
    return user


@user_view.route("/login/", methods=["GET", "POST", "DELETE", "PUT"])
def login_page():
    if current_user.is_authenticated is True:
        logout_user()
    login_url = url_prefix + "/login/password/"
    if "next" in request.args:
        next_url = request.args["next"]
    else:
        next_url = "/"
    if "rf" in request.headers and request.headers["rf"] == "async":
        return make_response("登录状态已过期，需要重新登录", 302)
    elif "rf" in request.args and request.args["rf"] == "async":
        return make_response("登录状态已过期，需要重新登录", 302)
    return rt.render("login_a.html", login_url=login_url, next_url=next_url)


login_manager.login_view = "user.login_page"


@user_view.route("/login/password/", methods=["POST"])
def login_action():
    rd = g.request_data
    user_name = rd["user_name"]
    password = rd["password"]
    next_url = rd["next"]
    r_code, item = c_user.user_confirm(g.session, password, user_name=user_name)
    if r_code == -3:
        return jsonify({"status": False, "data": "内部错误"})
    elif r_code == -2:
        return jsonify({"status": False, "data": "账号不存在"})
    elif r_code == -1:
        return jsonify({"status": False, "data": "密码不正确"})

    user = FlaskUser()
    user.user_no = item["user_no"]
    session["role"] = item["role"]
    login_user(user, remember=True)
    if len(next_url) == 0:
        next_url = "/"
    data = dict(location=next_url, user_name=item["user_name"])
    return jsonify({"status": True, "data": data})


@user_view.route("/login/wx/", methods=["POST"])
def wx_login_action():
    LOG.info('someone try login from wx')
    rd = g.request_data
    code = rd["code"]
    LOG.info('someone login from wx, code is %s', code)
    exec_r, data = mp.code2session(code)
    if exec_r is False:
        LOG.error('someone login from wx, code has error: %s', data)
        return jsonify({"status": False, "data": data})
    items = c_user.verify_user_exist(g.session, wx_id=data["openid"])
    if len(items) <= 0:
        LOG.info('someone login from wx, user not exist, new user %s', data["openid"])
        item = c_user.new_wx_user(data["openid"])
        c_user.generate_user_qr(item["user_no"])
    else:
        item = items[0]
    if item is None:
        LOG.error('someone login from wx, code has error: %s', data)
        return jsonify({"status": False, "data": "内部错误"})
    user = FlaskUser()
    user.user_no = item["user_no"]
    session["role"] = item["role"]
    login_user(user)
    LOG.info('%s login success from wx', user.user_no)
    return jsonify({"status": True, "data": item})


@user_view.route("/password/", methods=["GET"])
def password_page():
    return rt.render("password.html", url_prefix=url_prefix)


@user_view.route("/password/", methods=["POST"])
def password_action():
    user = request.form["user_name"]
    old_password = request.form["old_password"]
    confirm_password = request.form["confirm_password"]
    new_password = request.form["new_password"]
    if confirm_password != new_password:
        return u"两次输入密码不一致"
    code, item = c_user.user_confirm(old_password, user=user)
    if code != 0:
        return u"密码不正确"
    user_name = item["user_name"]
    c_user.update_password(user_name, new_password)
    return redirect(url_prefix + "/login/")


@user_view.route("/info/", methods=["GET"])
@login_required
def user_info():
    items = c_user.verify_user_exist(g.session, user_no=g.user_no)
    return jsonify({"status": True, "data": items})


@user_view.route("/info/", methods=["PUT"])
@login_required
def update_info_action():
    data = g.request_data
    c_user.update_info(g.user_no, **data)
    items = c_user.verify_user_exist(g.session, user_no=g.user_no)
    if len(items) <= 0:
        return jsonify({"status": False, "data": "not exist"})
    return jsonify({"status": True, "data": items[0]})


@user_view.route("/username", methods=["PUT"])
@login_required
def update_username_action():
    data = g.request_data
    password = data['password']
    if 'user_name' in data:
        user_name = data['user_name']
        v_r = c_user.verify_user_name_exist(user_name)
        if v_r:
            return jsonify({"status": False, "data": '账户名已存在'})
        c_user.set_username(g.user_no, user_name, password)
        items = c_user.verify_user_exist(g.session, user_no=g.user_no)
        if len(items) <= 0:
            return jsonify({"status": False, "data": "账户不存在"})
        user_data = items[0]
        if user_data['user_name'] is None:
            return jsonify({"status": False, "data": "设置账户名失败"})
        if user_data['user_name'] != user_name:
            return jsonify({"status": False, "data": "不允许修改账户名"})
        return jsonify({"status": True, "data": items[0]})
    else:
        items = c_user.verify_user_exist(g.session, user_no=g.user_no)
        if len(items) <= 0:
            return jsonify({"status": False, "data": "账户不存在"})
        user_data = items[0]
        if user_data['user_name'] is None:
            return jsonify({"status": False, "data": "未设置账户名，不允许设置密码"})
        c_user.update_password(user_data['user_name'], password)
        return jsonify({"status": True, "data": user_data})


@user_view.route("/whoIam/", methods=["GET"])
@login_required
def who_i_am_action():
    items = c_user.verify_user_exist(g.session, user_no=g.user_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "not exist"})
    en_s = c_user.who_i_am(g.user_no, 60)
    user_item = items[0]
    user_item["shy_me"] = en_s
    return jsonify({"status": True, "data": user_item})


@user_view.route("/whoIsHe/", methods=["POST"])
@login_required
def who_is_he_action():
    en_user = g.request_data["en_user"]
    user_no = c_user.who_is_he(en_user)
    if user_no is None:
        return jsonify({"status": False, "data": "无效的用户信息"})
    items = c_user.verify_user_exist(g.session, user_no=user_no)
    if len(items) <= 0:
        return jsonify({"status": False, "data": "用户不存在"})
    user_item = items[0]
    if user_item["user_no"] == g.user_no:
        user_item["is_self"] = True
    else:
        user_item["is_self"] = False
    return jsonify({"status": True, "data": user_item})


@user_view.route("/qr/", methods=["GET"])
def my_qr_code_png():
    user_no = c_user.who_is(request.args["whoIs"])
    if user_no is None:
        return make_response("Not Found", 404)
    d, f = c_user.my_qc_code(user_no)
    return send_from_directory(d, f)


@user_view.route('/nicknames', methods=['POST'])
@login_required
def get_multi_nickname():
    data = request.json
    items = c_user.get_multi_nick_name(user_list=data['user_list'])
    return jsonify({'status': True, 'data': items})

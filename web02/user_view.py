# !/usr/bin/env python
# coding: utf-8
import base64
from flask import g, jsonify, session, request, redirect, make_response, send_file, send_from_directory
from flask_login import UserMixin, login_user, current_user, logout_user, login_required
from flask_helper import RenderTemplate
from zh_config import db_conf_path, web_pro, min_program_conf, upload_folder
from classes.user import User
from classes.wx import MiniProgram
from web02 import create_blue, login_manager

__author__ = 'meisa'

url_prefix = "/user"
rt = RenderTemplate("user")
c_user = User(db_conf_path=db_conf_path, upload_folder=upload_folder)
mp = MiniProgram(conf_path=min_program_conf, section=web_pro)
user_view = create_blue("user", url_prefix=url_prefix, auth_required=False,
                        menu_list=[{"index": -2, "url": "/password/", "title": u"密码修改"},
                                   {"index": -1, "url": "/login/", "title": u"退出"}])


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


@user_view.route("/login/", methods=["GET"])
def login_page():
    if current_user.is_authenticated is True:
        logout_user()
    login_url = url_prefix + "/login/"
    if "next" in request.args:
        next_url = request.args["next"]
    else:
        next_url = "/"
    if "rf" in request.headers and request.headers["rf"] == "async":
        return make_response("登录状态已过期，需要重新登录", 302)
    elif "rf" in request.args and request.args["rf"] == "async":
        return make_response("登录状态已过期，需要重新登录", 302)
    return rt.render("login.html", login_url=login_url, next_url=next_url)


login_manager.login_view = "user.login_page"


@user_view.route("/login/", methods=["POST"])
def login_action():
    rd = g.request_data
    user_name = rd["user_name"]
    password = rd["password"]
    next_url = rd["next"]
    r_code, item = c_user.user_confirm(password, user_name=user_name)
    if r_code == -3:
        return jsonify({"status": False, "data": "内部错误"})
    elif r_code == -2:
        return jsonify({"status": False, "data": "账号不存在"})
    elif r_code == -1:
        return jsonify({"status": False, "data": "密码不正确"})

    user = FlaskUser()
    user.user_no = item["user_no"]
    login_user(user, remember=True)
    if len(next_url) == 0:
        next_url = "/"
    data = dict(location=next_url, user_name=item["user_name"])
    return jsonify({"status": True, "data": data})


@user_view.route("/login/wx/", methods=["POST"])
def wx_login_action():
    rd = g.request_data
    code = rd["code"]
    exec_r, data = mp.code2session(code)
    if exec_r is False:
        return jsonify({"status": False, "data": data})
    items = c_user.verify_user_exist(wx_id=data["openid"])
    if len(items) <= 0:
        item = c_user.new_wx_user(data["openid"])
        c_user.generate_user_qr(item["user_no"])
    else:
        item = items[0]
    if item is None:
        return jsonify({"status": False, "data": "内部错误"})
    user = FlaskUser()
    user.user_no = item["user_no"]
    login_user(user)
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
    items = c_user.verify_user_exist(user_no=g.user_no)
    return jsonify({"status": True, "data": items})


@user_view.route("/info/", methods=["PUT"])
@login_required
def update_info_action():
    data = g.request_data
    c_user.update_info(g.user_no, **data)
    items = c_user.verify_user_exist(user_no=g.user_no)
    if len(items) <= 0:
        return jsonify({"status": False, "data": "not exist"})
    return jsonify({"status": True, "data": items[0]})


@user_view.route("/whoIam/", methods=["GET"])
@login_required
def who_i_am_action():
    items = c_user.verify_user_exist(user_no=g.user_no)
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
    items = c_user.verify_user_exist(user_no=user_no)
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

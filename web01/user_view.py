# !/usr/bin/env python
# coding: utf-8

from flask import g, jsonify, session, request, redirect
from flask_login import UserMixin, login_user, current_user, logout_user, login_required
from flask_helper import RenderTemplate
from zh_config import db_conf_path
from classes.user import User
from web01 import create_blue, login_manager

__author__ = 'meisa'

url_prefix = "/user"
rt = RenderTemplate("user")
c_user = User(db_conf_path=db_conf_path)
user_view = create_blue("user", url_prefix=url_prefix, auth_required=False,
                        menu_list=[{"index": -2, "url": "/password/", "title": u"密码修改"},
                                   {"index": -1, "url": "/login/", "title": u"退出"}])


class FlaskUser(UserMixin):
    user_name = ""

    def get_id(self):
        return self.user_name


@login_manager.user_loader
def load_user(user_name):
    user = FlaskUser()
    user.user_name = user_name
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
    user.user_name = item["user_name"]
    login_user(user)
    if len(next_url) == 0:
        next_url = "/"

    data = dict(location=next_url, user_name=item["user_name"])
    return jsonify({"status": True, "data": data})


@user_view.route("/password/", methods=["GET"])
def password_page():
    return rt.render("password.html", url_prefix=url_prefix)


@user_view.route("/password/", methods=["POST"])
def password_action():
    user_name = request.form["user_name"]
    old_password = request.form["old_password"]
    confirm_password = request.form["confirm_password"]
    new_password = request.form["new_password"]
    if confirm_password != new_password:
        return u"两次输入密码不一致"
    code, item = c_user.user_confirm(old_password, user_name=user_name)
    if code != 0:
        return u"密码不正确"
    c_user.update_password(user_name, new_password)
    return redirect(url_prefix + "/login/")
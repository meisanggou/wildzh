# !/usr/bin/env python
# coding: utf-8

import os
import sys
from flask import request, g, make_response, Blueprint, jsonify, session
from flask_login import current_user, UserMixin, LoginManager

from tools import JYFlask
from function import normal_request_detection, make_static_html, make_default_static_url, make_static_url
from function import make_static_html2

__author__ = 'zhouheng'


class User(UserMixin):
    user_name = ""

    def get_id(self):
        return self.user_name

login_manager = LoginManager()
login_manager.session_protection = 'strong'


@login_manager.user_loader
def load_user(user_name):
    user = User()
    user.user_name = user_name
    if "roles" in session:
        user.roles = session["roles"]
    else:
        user.roles = None
        session["roles"] = None
    if "role" in session:
        user.role = session["role"]
    else:
        user.role = 0
        session["role"] = user.role
    return user


def create_app():
    one_web = JYFlask(__name__)

    one_web.secret_key = 'a string'
    login_manager.init_app(one_web)

    @one_web.before_request
    def before_request():
        test_r, info = normal_request_detection(request.headers, request.remote_addr)
        if test_r is False:
            return make_response(info, 403)
        g.request_IP_s, g.request_IP = info
        if current_user.is_authenticated:
            g.user_role = current_user.role
            g.user_name = current_user.user_name
            g.user_roles = current_user.roles
            # if g.user_name in user_blacklist:
            #     message =u"不好意思，您的帐号存在异常，可能访问本系统出现不稳定的想象，现在就是不稳定中。本系统不是很智能，所以不知道啥时候会稳定，也许一分钟，也许一天，也许。。。"
            #     if "X-Requested-With" in request.headers:
            #         return jsonify({"status": False, "data": message})
            #     return message
        else:
            g.user_role = 0
        if "Accept" in request.headers and request.headers["Accept"].find("application/json") >= 0:
            g.accept_json = True
        else:
            g.accept_json = False

    @one_web.after_request
    def after_request(res):
        if res.status_code == 302 or res.status_code == 301:
            if "X-Request-Protocol" in request.headers:
                pro = request.headers["X-Request-Protocol"]
                if "Location" in res.headers:
                    location = res.headers["location"]
                    if location.startswith("http:"):
                        res.headers["Location"] = pro + ":" + res.headers["Location"][5:]
                    elif location.startswith("/"):
                        res.headers["Location"] = "%s://%s%s" % (pro, request.headers["Host"], location)
        if "download_file" in g:
            try:
                os.system("rm -rf %s" % g.download_file)
            except Exception as e:
                print(e)
        res.headers["Server"] = "JingYun Server"
        return res

    @one_web.errorhandler(500)
    def handle_500(e):
        return str(e)

    one_web.add_url_rule("/static00" + '/<path:filename>', endpoint='static00', view_func=one_web.send_static_file2,
                         defaults=dict(static_folder=os.path.join(os.path.split(os.path.dirname(__file__))[0], "static")))
    one_web.static_folder = "static"
    one_web.add_url_rule("/static01" + '/<path:filename>', endpoint='static01', view_func=one_web.send_static_file)
    one_web.config.update(PERMANENT_SESSION_LIFETIME=600)

    env = one_web.jinja_env
    # env.globals["current_env"] = current_env
    # env.globals["role_value"] = control.role_value
    # env.globals["menu_url"] = dms_url_prefix + "/portal/"
    # env.globals["short_link_url"] = short_link_prefix
    # env.filters['unix_timestamp'] = unix_timestamp
    # env.filters['bit_and'] = bit_and
    # env.filters['ip_str'] = ip_str
    env.filters['make_static_url'] = make_static_url
    env.filters['make_default_static_url'] = make_default_static_url
    env.filters['make_static_html'] = make_static_html
    env.filters['make_static_html2'] = make_static_html2
    return one_web

app = create_app()


def create_blue(blue_name, url_prefix="/", auth_required=True, special_protocol=False):
    add_blue = Blueprint(blue_name, __name__, url_prefix=url_prefix)
    # if auth_required:
    #     @add_blue.before_request
    #     @login_required
    #     def before_request():
    #         if special_protocol is True:
    #             r_protocol = request.headers.get("X-Request-Protocol", "http")
    #             if r_protocol not in request_special_protocol:
    #                 redirect_url = "%s://%s%s" % (request_special_protocol[0], request.host, request.full_path)
    #                 return redirect(redirect_url)
    #
    #         g.role_value = control.role_value

    def ping():
        return jsonify({"status": True, "message": "ping %s success" % request.path})

    add_blue.add_url_rule("/ping/", endpoint="%s_ping" % blue_name, view_func=ping)
    app.blues.append(add_blue)
    # current_app.before_request_funcs[blue_name] = before_request_funcs
    return add_blue
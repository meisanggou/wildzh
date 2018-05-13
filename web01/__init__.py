# !/usr/bin/env python
# coding: utf-8

import os
import sys
from flask import request, g, make_response, Blueprint, jsonify
from flask_login import current_user, LoginManager, login_required

from flask_helper import Flask2
from zh_config import file_prefix_url, upload_folder
from function import normal_request_detection, make_static_html, make_default_static_url, make_static_url
from function import make_static_html2

__author__ = 'zhouheng'


login_manager = LoginManager()
login_manager.session_protection = 'strong'


def create_app():
    one_web = Flask2(__name__)

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
    one_web.add_url_rule(file_prefix_url + "/<path:filename>", endpoint="file", view_func=one_web.send_static_file2,
                         defaults=dict(static_folder=upload_folder))
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
    if auth_required:
        @add_blue.before_request
        @login_required
        def before_request():
            pass

    def ping():
        return jsonify({"status": True, "message": "ping %s success" % request.path})

    add_blue.add_url_rule("/ping/", endpoint="%s_ping" % blue_name, view_func=ping)
    app.blues.append(add_blue)
    # current_app.before_request_funcs[blue_name] = before_request_funcs
    return add_blue
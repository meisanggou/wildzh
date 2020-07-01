# !/usr/bin/env python
# coding: utf-8

import os
import functools

from flask import request, g, Blueprint, jsonify
from flask_login import current_user, LoginManager, login_required
from flask_helper import Flask2

from zh_config import file_prefix_url, upload_folder, accept_agent
from wildzh.function.web_func import make_static_html, make_default_static_url, make_static_url
from wildzh.function.web_func import make_static_html2
from wildzh.utils.log import getLogger

__author__ = 'zhouheng'


login_manager = LoginManager()
login_manager.session_protection = 'strong'
LOG = getLogger()


def create_app():
    one_web = Flask2(__name__)

    one_web.secret_key = 'a string'
    login_manager.init_app(one_web)

    @one_web.before_request
    def before_request():
        if current_user.is_authenticated:
            g.user_role = current_user.role
            g.user_no = current_user.user_no
            LOG.info('receive request: user:%s role:%s method:%s full_path:%s',
                     g.user_no, g.user_role, request.method, request.full_path)
        else:
            g.user_role = 0
            g.user_no = None
        if "Accept" in request.headers and request.headers["Accept"].find("application/json") >= 0:
            g.accept_json = True
        else:
            g.accept_json = False

    @one_web.after_request
    def after_request(res):
        if "download_file" in g:
            try:
                os.system("rm -rf %s" % g.download_file)
            except Exception as e:
                print(e)
        res.headers["Server"] = "Wild Server"
        return res

    one_web.add_url_rule("/static00" + '/<path:filename>', endpoint='static00', view_func=one_web.send_static_file2,
                         defaults=dict(static_folder=os.path.join(os.path.split(os.path.dirname(__file__))[0], "static")))
    one_web.static_folder = "static"
    one_web.add_url_rule("/static01" + '/<path:filename>', endpoint='static01', view_func=one_web.send_static_file)
    one_web.add_url_rule(file_prefix_url + "/<path:filename>", endpoint="file", view_func=one_web.send_static_file2,
                         defaults=dict(static_folder=upload_folder))
    one_web.config.update(PERMANENT_SESSION_LIFETIME=3600)

    env = one_web.jinja_env
    # env.globals["current_env"] = current_env
    # env.globals["role_value"] = control.role_value
    # env.globals["menu_url"] = "/"
    # env.globals["short_link_url"] = short_link_prefix
    # env.filters['unix_timestamp'] = unix_timestamp
    # env.filters['bit_and'] = bit_and
    # env.filters['ip_str'] = ip_str
    env.filters['make_static_url'] = make_static_url
    env.filters['make_default_static_url'] = make_default_static_url
    env.filters['make_static_html'] = make_static_html
    env.filters['make_static_html2'] = make_static_html2
    env.variable_start_string = "{{ "
    env.variable_end_string = " }}"

    one_web.handle_30x()
    one_web.cross_domain()
    one_web.filter_user_agent(accept_agent)
    return one_web

app = create_app()

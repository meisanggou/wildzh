# !/usr/bin/env python
# coding: utf-8

import os

from werkzeug.exceptions import HTTPException

from flask import request, g, redirect, make_response, jsonify
from flask_login import LoginManager
from flask_login.utils import login_url as make_login_url
from flask_helper import Flask2

from zh_config import file_prefix_url, upload_folder
from wildzh.function.web_func import make_static_html, make_default_static_url, make_static_url
from wildzh.function.web_func import make_static_html2
from wildzh.utils.log import getLogger

__author__ = 'zhouheng'


login_manager = LoginManager()
login_manager.session_protection = 'strong'  # TODO 原来是basic 可行吗？
LOG = getLogger()

class _Flask2(Flask2):

    def request_context(self, environ):
        method_header = 'X-Request-Method'
        _header = 'HTTP_%s' % method_header.upper()
        req_method = None
        if _header in environ:
            req_method = environ[_header]
        elif 'headers_raw' in environ:
            for header in environ['headers_raw']:
                if header[0] == method_header:
                    req_method = header[1]
                    break
        if req_method in ['GET', 'POST', 'DELETE']:
            environ['REQUEST_METHOD'] = req_method

        req = super().request_context(environ)
        return req


def create_app():
    one_web = _Flask2(__name__, log=LOG)

    one_web.secret_key = 'a string'
    login_manager.init_app(one_web)
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.headers.get('X-REQ-API'):
            return make_response('Unauthorized', 401)
        redirect_url = make_login_url(login_manager.login_view,
                                      next_url=request.url)
        return redirect(redirect_url)

    @one_web.before_request
    def before_request():
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
        LOG.info('receive request: [%s][%s][%s][%s] full_path:%s '
                 'user-agent:%s', res.status_code, request.method,
                 getattr(g, 'remote_addr', None),
                 getattr(g, 'user_no', None),
                 request.full_path,
                 request.headers.get('User-Agent'))
        return res

    @one_web.errorhandler(Exception)
    @one_web.errorhandler(HTTPException)
    @one_web.errorhandler(500)
    def handle_500(e):
        if isinstance(e, HTTPException):
            response = jsonify({'status': False, 'data': e.description})
            response.status_code = e.code
            return response
        LOG.exception(e)
        return jsonify({'status': False, 'data': 'Internal error'})

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
    one_web.real_ip()
    # one_web.cross_domain()
    ignore_paths = [".+\.jpeg", ".+\.png"]
    # one_web.filter_user_agent(accept_agent, ignore_paths=ignore_paths)
    return one_web

app = create_app()

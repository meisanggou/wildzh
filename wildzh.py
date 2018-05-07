# !/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.append("..")
from flask import Flask, request, g, make_response, current_app
from flask_login import current_user

from function import normal_request_detection
from zh_config import web_pro

__author__ = 'zhouheng'


def create_app():
    one_web = Flask(__name__)

    one_web.secret_key = 'a string'
    # login_manager.init_app(one_web)

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

    # one_web.static_folder = "static2"
    # if static_prefix_url.startswith("/"):
    #     one_web.add_url_rule(static_prefix_url + '/<path:filename>', endpoint='static2',
    #                          view_func=one_web.send_static_file)
    one_web.config.update(PERMANENT_SESSION_LIFETIME=600)
    app_dir = os.path.split(os.path.abspath(__file__))[0]
    view_files = os.listdir(os.path.join(app_dir, "web%s" % web_pro, "views"))
    for view_file in view_files:
        if view_file.endswith("_view.py"):
            print("start import")
            __import__("web01.views.%s" % view_file[:-3])

    # from Web import blues
    # for key, value in blues.items():
    #     if len(value[1]) > 1:
    #         one_web.register_blueprint(value[0], url_prefix=value[1])
    #     else:
    #         one_web.register_blueprint(value[0])

    env = one_web.jinja_env
    # env.globals["current_env"] = current_env
    # env.globals["role_value"] = control.role_value
    # env.globals["menu_url"] = dms_url_prefix + "/portal/"
    # env.globals["short_link_url"] = short_link_prefix
    # env.filters['unix_timestamp'] = unix_timestamp
    # env.filters['bit_and'] = bit_and
    # env.filters['ip_str'] = ip_str
    # env.filters['make_static_url'] = make_static_url
    # env.filters['make_default_static_url'] = make_default_static_url
    # env.filters['make_static_html'] = make_static_html
    print()
    return one_web

app = create_app()

if __name__ == '__main__':
    app.run()

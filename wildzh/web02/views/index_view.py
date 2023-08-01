# !/usr/bin/env python
# coding: utf-8
from flask import jsonify, redirect
from flask import g
from flask import request
from flask_helper.template import RenderTemplate

from wildzh.utils import datetime_helper
from wildzh.utils.log import getLogger
from wildzh.classes.version import VersionMP
from wildzh.web02.view import View2


__author__ = 'meisa'

menu_list = {"title": u"首页", "icon_class": "icon-shouye", "menu_id": "home", "index": 0}
rt = RenderTemplate()
index_view = View2("index", __name__, url_prefix="/", menu_list=menu_list)
index_view.register_jinja_global_env('menu_url', '/')
LOG = getLogger()
VERSION_MAN = VersionMP()


@index_view.route("/", methods=["GET"])
def index():
    return redirect("/exam/")


@index_view.route('/version/wx', methods=['POST'])
def report_wx_min_program_version():
    data = request.json
    version = data['version']
    r = False
    if g.user_no:
        VERSION_MAN.update_version(g.session, g.user_no, version)
        r = True
    LOG.info('Receive user(user_no=%s) report wx min_program version: %s',
             g.user_no, version)
    return jsonify({'status': r, 'data': data})


@index_view.route('/qian', methods=['GET'])
def qian_page():
    from datetime import datetime
    items = []
    dt1 = datetime(1993, 8, 2)
    dt2 = datetime(1994, 7, 31)
    dt3 = datetime(2023, 3, 31, 11, 18)
    for dt in (dt1, dt2, dt3):
        data = datetime_helper.calc_ymd(datetime.now(), dt)
        items.append(data)

    return rt.render('qian.html', items=items)

#! /usr/bin/env python
# coding: utf-8

import os
import re
from time import time
from functools import wraps
from flask import request, g, jsonify
from flask_login import login_required
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, upload_folder, file_prefix_url
from classes.insider import Insider
from web01 import create_blue

__author__ = 'ZhouHeng'

url_prefix = "/insider"

rt = RenderTemplate("insider", url_prefix=url_prefix)
insider_view = create_blue('insider_view', url_prefix=url_prefix, auth_required=True)
c_insider = Insider(db_conf_path)


@insider_view.route("/project/", methods=["GET"])
def get_my_project():
    items = c_insider.select_my_project(user_no=g.user_no)
    return jsonify({"status": True, "data": items})


@insider_view.route("/project/", methods=["POST"])
def new_project_action():
    project_name = request.json["project_name"]
    exec_r, data = c_insider.new_project(g.user_no, project_name)
    return jsonify({"status": exec_r, "data": data})


@insider_view.route("/recharge/", methods=["POST"])
def recharge_action():
    # 商家扫描用户 获得用户user_no 为其充值
    data = g.request_data
    project_no = data["project_no"]

    return jsonify({"status": True, "data": []})
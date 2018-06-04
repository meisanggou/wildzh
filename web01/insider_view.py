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
    if exec_r is True:
        project_no = data["project_no"]
        save_path = os.path.join(upload_folder, "insider", "project", "%s_qr.png" % project_no)
        c_insider.create_project_qr(project_no, save_path)
    return jsonify({"status": exec_r, "data": data})


@insider_view.route("/project/mine/", methods=["GET"])
def mine_info_in_project():
    project_no = request.args["project_no"]
    items = c_insider.select_project(project_no=project_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "项目不存在"})
    pro_item = items[0]
    items = c_insider.select_member(project_no, g.user_no)
    if len(items) != 1:
        pro_item["is_member"] = False
    else:
        pro_item["is_member"] = True
        pro_item.update(items[0])
    return jsonify({"status": True, "data": pro_item})


support_upload2(insider_view, upload_folder, file_prefix_url, ("insider", "project"), "upload/p")


@insider_view.route("/recharge/", methods=["POST"])
def recharge_action():
    # 商家扫描用户 获得用户user_no 为其充值
    data = g.request_data
    project_no = data["project_no"]
    user_no = int(data["user_no"])
    amount = int(data["amount"])
    # 验证用户是否有权限充值
    items = c_insider.select_project(project_no=project_no, owner=g.user_no)
    if len(items) <= 0:
        return jsonify({"status": True, "data": "用户无权限充值"})
    exec_r, data = c_insider.new_pay(project_no, user_no, 1, amount, "充值")
    return jsonify({"status": exec_r, "data": data})


@insider_view.route("/pay/", methods=["POST"])
def pay_action():
    # 商家扫描用户 获得用户user_no 为其充值
    data = g.request_data
    project_no = data["project_no"]
    amount = int(data["amount"])
    exec_r, data = c_insider.new_pay(project_no, g.user_no, 101, amount, "消费")
    return jsonify({"status": exec_r, "data": data})
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
from classes.comment import Comment
from web01 import create_blue

__author__ = 'ZhouHeng'

url_prefix = "/comment"

rt = RenderTemplate("comment", url_prefix=url_prefix)
comment_view = create_blue('comment_view', url_prefix=url_prefix, auth_required=False)
c_comment = Comment(db_conf_path)


@comment_view.route("/", methods=["GET"])
def get_my_project():
    resource_id = request.args["resource_id"]
    items = c_comment.select_comment(resource_id=resource_id)
    return jsonify({"status": True, "data": items})


@comment_view.route("/", methods=["POST"])
def new_project_action():
    g.user_no = 1
    data = g.request_data
    resource_id = data["resource_id"]
    if len(resource_id) != 35:
        return jsonify({"status": False, "data": "resource id length must be 35"})
    content = data["content"]
    comment_id = data.get("comment_id", None)
    anonymous = data.get("anonymous", False)
    if anonymous not in [True, False]:
        return jsonify({"status": False, "data": "invalid anonymous"})
    exec_r, data = c_comment.new_comment(resource_id, content, g.user_no, comment_id)
    return jsonify({"status": exec_r, "data": data})

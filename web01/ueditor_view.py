#! /usr/bin/env python
# coding: utf-8

import os
import base64
from time import time
from random import randint
from datetime import datetime
from flask import request, send_from_directory, g, jsonify
from flask_helper import RenderTemplate
from web01 import create_blue, upload_folder

__author__ = 'ZhouHeng'

url_prefix = "/editor"
rt = RenderTemplate("UEditor", url_prefix=url_prefix)
editor_view = create_blue('editor_view', url_prefix=url_prefix, auth_required=True)

upload_data_dirs = {"image": "img", "scrawl": "scrawl"}

for key in upload_data_dirs:
    key_dir = os.path.join(upload_folder, upload_data_dirs[key])
    if os.path.isdir(key_dir) is False:
        os.mkdir(key_dir)


@editor_view.route("/")
def demo_func():
    title = None
    if "title" in request.args:
        title = request.args["title"]
    return rt.render("demo.html", h_title=title)


@editor_view.route("/config/", methods=["GET"])
def config_func():
    # action = request.args["action"]
    return rt.render("config.json")


def get_date_dir(parent_dir):
    now_date = datetime.now()
    date_dir = "%s/%s%s" % (parent_dir, now_date.year, now_date.month)
    if os.path.isdir(os.path.join(upload_folder, date_dir)) is False:
        os.makedirs(os.path.join(upload_folder, date_dir))
    return date_dir


def generate_file_path(account, file_type=None):
    file_path = account
    file_path += "_%s" % randint(100, 999)
    file_path += "_%s" % int(time())
    if file_type is not None:
        file_path += ".%s" % file_type
    return file_path


@editor_view.route("/config/", methods=["POST"])
def action_config():
    action = request.args["action"]
    if action == "uploadimage":
        img_file = request.files["upfile"]
        file_type = img_file.filename.rsplit(".", 1)[-1]
        save_file_name = get_date_dir(upload_data_dirs["image"]) + "/" + generate_file_path(g.user_no, file_type)
        save_path = os.path.join(upload_folder, save_file_name)
        img_file.save(os.path.join(save_path))
        title = img_file.filename
    elif action == "uploadscrawl":
        file_type = "jpg"
        save_file_name = get_date_dir(upload_data_dirs["scrawl"]) + "/" + generate_file_path(g.user_no, file_type)
        save_path = os.path.join(upload_folder, save_file_name)
        with open(save_path, "wb") as ws:
            ws.write(base64.b64decode(request.form["upfile"]))
        title = ""
    else:
        return jsonify({"state": "FAIL"})
    file_size = os.path.getsize(save_path)
    return jsonify({"state": "SUCCESS", "url": "%s/upload/%s" % (url_prefix, save_file_name), "title": title,
                    "size": file_size, "type": ".%s" % file_type})


def send_editor_static_file(filename):
    return send_from_directory("ueditor", filename)


def send_editor_upload_file(filename):
    return send_from_directory(upload_folder, filename)


editor_view.add_url_rule('/<path:filename>', endpoint='ueditor', view_func=send_editor_static_file)
editor_view.add_url_rule('/upload/<path:filename>', endpoint='', view_func=send_editor_upload_file)

# !/usr/bin/env python
# coding: utf-8
import os
import re
import uuid
import string
from functools import wraps
from werkzeug.utils import secure_filename
from flask import request, jsonify, g
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, upload_folder, file_prefix_url
from tools import folder
from classes.music import Music
from web01 import create_blue

__author__ = 'meisa'

url_prefix = "/music"

rt = RenderTemplate("music")
music_view = create_blue("music", url_prefix=url_prefix)
c_music = Music(db_conf_path)
music_upload_folder = os.path.join(upload_folder, "music")
pic_folder = folder.create_folder2(music_upload_folder, "pic")
music_folder = folder.create_folder2(music_upload_folder, "m")


def refer_music_no(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Referer" not in request.headers:
            return jsonify({"status": False, "data": "Bad Request"})
        g.ref_url = request.headers["Referer"]
        find_no = re.findall("music_no=(\\d+)", g.ref_url)
        if len(find_no) > 0:
            g.music_no = find_no[0]
        elif "music_no" in request.args:
            g.music_no = request.args["music_no"]
        else:
            g.music_no = None
        return f(*args, **kwargs)
    return decorated_function


def required_music_no(f):
    @wraps(f)
    @refer_music_no
    def decorated_function(*args, **kwargs):
        if g.music_no is None:
            return jsonify({"status": False, "data": "Bad Request"})
        return f(*args, **kwargs)
    return decorated_function


@music_view.route("/", methods=["GET"])
def index():
    add_url = url_prefix + "/"
    upload_url = url_prefix + "/upload/"
    m_upload_url = url_prefix + "/upload/m/"
    info_url = url_prefix + "/info/"
    online_url = url_prefix + "/online/"
    page_music = url_prefix + "/?action=music"
    page_list = url_prefix + "/"
    if "action" in request.args and request.args["action"] == "music":
        return rt.render("entry_info.html", page_list=page_list, add_url=add_url, upload_url=upload_url,
                         m_upload_url=m_upload_url)
    if "music_no" in request.args:
        return rt.render("detail.html",page_list=page_list, page_music=page_music, info_url=info_url)
    return rt.render("overview.html", page_music=page_music, info_url=info_url, online_url=online_url)


@music_view.route("/", methods=["POST"])
def new_music():
    g.user_name = "zh_test"
    data = g.request_data
    r, music_no = c_music.new_music(data["music_name"], data["music_type"], data["music_desc"], data["music_url"],
                                 g.user_name, pic_url=data["pic_url"])
    if r is False:
        return jsonify({"status": False, "data": "请重试"})
    data["music_no"] = music_no
    return jsonify({"status": True, "data": data})


support_upload2(music_view, upload_folder, file_prefix_url, ("music", "pic"), "upload")
support_upload2(music_view, upload_folder, file_prefix_url, ("music", "m"), "upload/m")


@music_view.route("/info/", methods=["GET"])
@refer_music_no
def get_music_info():
    find_type = re.findall("music_type=(\\w+)", g.ref_url)
    if len(find_type) > 0:
        music_type = find_type[0]
    elif "music_type" in request.args:
        music_type = request.args["music_type"]
    else:
        music_type = None
    items = c_music.select_music(music_type, g.music_no)
    return jsonify({"status": True, "data": items})


@music_view.route("/info/", methods=["DELETE"])
def delete_music():
    music_no = g.request_data["music_no"]
    music_type = g.request_data["music_type"]
    l = c_music.delete_music(music_type, music_no)
    return jsonify({"status": True, "data": "删除成功"})



@music_view.route("/online/", methods=["POST"])
def online_music():
    music_no = g.request_data["music_no"]
    music_type = g.request_data["music_type"]
    items = c_music.select_music(music_type, music_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "音乐不存在"})
    c_music.online_music(music_no)
    return jsonify({"status": True, "data": "success"})


@music_view.route("/records/", methods=["POST"])
def add_music_records():
    data = g.request_data
    music_type = data["music_type"]
    music_no = data["music_no"]
    user_id = data["user_id"]
    progress = data["progress"]
    c_music.new_music_record(user_id, music_no, progress)
    return jsonify({"status": True, "data": "success"})

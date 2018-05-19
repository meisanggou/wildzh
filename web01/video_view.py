# !/usr/bin/env python
# coding: utf-8
import os
import re
import string
from functools import wraps
from flask import request, jsonify, g
from flask_login import login_required
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, upload_folder, file_prefix_url
from classes.video import Video
from web01 import create_blue

__author__ = 'meisa'

url_prefix = "/video"

rt = RenderTemplate("video")
video_view = create_blue("video", url_prefix=url_prefix, auth_required=False, menu_list={"title": u"视频管理"})
c_video = Video(db_conf_path)


def referer_video_no(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Referer" not in request.headers:
            g.ref_url = ""
            g.video_no = None
        else:
            g.ref_url = request.headers["Referer"]
        find_no = re.findall("video_no=(\\w+)", g.ref_url)
        if len(find_no) > 0:
            g.video_no = find_no[0]
        elif "video_no" in request.args:
            g.video_no = request.args["video_no"]
        else:
            g.video_no = None
        return f(*args, **kwargs)
    return decorated_function


def required_video_no(f):
    @wraps(f)
    @referer_video_no
    def decorated_function(*args, **kwargs):
        if g.video_no is None:
            return jsonify({"status": False, "data": "Bad Request"})
        return f(*args, **kwargs)
    return decorated_function


@video_view.route("/", methods=["GET"])
@login_required
def index():
    upload_url = url_prefix + "/upload/"
    url_upload_e = url_prefix + "/upload/e/"
    info_url = url_prefix + "/info/"
    online_url = url_prefix + "/online/"
    url_episode = url_prefix + "/episode/"
    page_video = url_prefix + "/?action=video"
    page_list = url_prefix + "/"
    if "action" in request.args and request.args["action"] == "video":
        return rt.render("entry_info.html", page_list=page_list, info_url=info_url, upload_url=upload_url,
                         page_video=page_video)
    if "video_no" in request.args:
        return rt.render("episode.html", page_list=page_list, page_video=page_video, info_url=info_url,
                         url_episode=url_episode, url_upload_e=url_upload_e, upload_url=upload_url)
    return rt.render("overview.html", page_video=page_video, info_url=info_url, online_url=online_url)


@video_view.route("/info/", methods=["POST"])
@login_required
def new_video():
    g.user_name = "zh_test"
    data = g.request_data
    r, video_no = c_video.new_video(data["video_name"], data["video_type"], data["video_desc"],
                                    data["episode_num"], data["video_pic"], g.user_name)
    if r is False:
        return jsonify({"status": False, "data": "请重试"})
    data["video_no"] = video_no
    return jsonify({"status": True, "data": data})


support_upload2(video_view, upload_folder, file_prefix_url, ("video", "pic"), "upload", rename_mode="sha1")
support_upload2(video_view, upload_folder, file_prefix_url, ("video", "episode"), "upload/e", rename_mode="sha1")


@video_view.route("/info/", methods=["GET"])
@referer_video_no
def get_video_info():
    find_type = re.findall("video_type=(\\w+)", g.ref_url)
    if len(find_type) > 0:
        video_type = find_type[0]
    elif "video_type" in request.args:
        video_type = request.args["video_type"]
    else:
        video_type = None
    items = c_video.select_video(video_type, g.video_no)
    if g.user_name is None:
        for i in range(len(items) - 1, -1, -1):
            if items[i]["status"] & 64 == 64:
                continue
            del items[i]
    return jsonify({"status": True, "data": items})


@video_view.route("/info/", methods=["PUT"])
@login_required
def update_video():
    data = g.request_data
    video_type = data.pop("video_type")
    video_no = data.pop("video_no")
    l = c_video.update_video(video_type, video_no, **data)
    return jsonify({"status": True, "data": g.request_data})


@video_view.route("/info/", methods=["DELETE"])
@login_required
def delete_video():
    video_no = g.request_data["video_no"]
    video_type = g.request_data["video_type"]
    l = c_video.delete_video(video_type, video_no)
    return jsonify({"status": True, "data": "删除成功"})


@login_required
@video_view.route("/episode/", methods=["POST", "PUT"])
@required_video_no
def entry_questions():
    find_type = re.findall("video_type=(\\w+)", g.ref_url)
    if len(find_type) > 0:
        video_type = find_type[0]
    elif "video_type" in request.args:
        video_type = request.args["video_type"]
    else:
        video_type = None
    data = g.request_data
    title = data["title"]
    episode_index = data["episode_index"]
    episode_pic = data["episode_pic"]
    episode_url = data["episode_url"]
    items = c_video.select_video(video_type, g.video_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "视频集不存在"})
    if episode_index >= items[0]["episode_num"]:
        return jsonify({"status": False, "data": "视频集索引超出总集数"})
    if request.method == "POST":
        r = True
        l = c_video.new_video_episode(video_type, g.video_no, episode_index, title, episode_url, episode_pic)
    else:
        l = c_video.update_video_questions(g.video_no, question_no, question_desc, select_mode, options)
        r = True
    return jsonify({"status": r, "data": dict(action=request.method, data=data)})


@video_view.route("/episode/", methods=["GET"])
@required_video_no
def get_video_questions():
    items = c_video.select_episode(g.video_no)

    return jsonify({"status": True, "data": items})


@video_view.route("/online/", methods=["POST"])
@login_required
def online_video():
    video_no = g.request_data["video_no"]
    video_type = g.request_data["video_type"]
    items = c_video.select_video(video_type, video_no)
    if len(items) != 1:
        return jsonify({"status": False, "data": "视频不存在"})
    if items[0]["status"] & 7 != 7:
        return jsonify({"status": False, "data": "视频状态未达到不可上线"})
    c_video.online_video(video_no)
    return jsonify({"status": True, "data": "success"})


@video_view.route("/records/", methods=["POST"])
def add_video_records():
    data = g.request_data
    video_type = data["video_type"]
    video_no = data["video_no"]
    user_id = data["user_id"]
    result = data["result"]
    c_video.new_video_record(user_id, video_no, result)
    explains = c_video.select_result_explain(video_no, result)
    tj = c_video.select_tj(video_no)
    r = dict(result=result)
    if len(tj) > 0:
        r["tj"] = tj[0]
    else:
        r["tj"] = None
    if len(explains) > 0:
        r["result_explain"] = explains[0]
    else:
        r["result_explain"] = None
    return jsonify({"status": True, "data": r})

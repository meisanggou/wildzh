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
video_view = create_blue("video", url_prefix=url_prefix, auth_required=False, menu_list={"title": u"音/视频集管理"})
c_video = Video(db_conf_path)

type_dict = dict(dongman=u"动漫",
                 yingshi=u"影视",
                 gxshipin=u"国学视频",
                 gxyinpin=u"国学音频",
                 jtshipin=u"家庭视频",
                 jtyinpin=u"家庭音频")
format_dict = [[u"视频", "video/mp4"], [u"音频", "audio/mp3"]]


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
    url_people = "/people/info/?group_id=media&online=true"
    url_people_resource = "/people/resource/"
    upload_url = url_prefix + "/upload/"
    url_upload_e = url_prefix + "/upload/e/"
    info_url = url_prefix + "/info/"
    online_url = url_prefix + "/online/"
    page_video = url_prefix + "/?action=video"
    page_list = url_prefix + "/"
    type_desc = u"音视频"
    if "video_type" in request.args and request.args["video_type"] in type_dict:
        video_type = request.args["video_type"]
        page_list += "?video_type=" + video_type
        page_video += "&video_type=" + video_type
        type_desc = type_dict[video_type]
    url_episode = url_prefix + "/episode/"

    if "action" in request.args and request.args["action"] == "video":
        return rt.render("entry_info.html", page_list=page_list, info_url=info_url, upload_url=upload_url,
                         page_video=page_video, type_dict=type_dict, format_dict=format_dict, url_people=url_people,
                         url_people_resource=url_people_resource, type_desc=type_desc)
    if "video_no" in request.args:
        return rt.render("episode.html", page_list=page_list, page_video=page_video, info_url=info_url,
                         url_episode=url_episode, url_upload_e=url_upload_e, upload_url=upload_url, type_dict=type_dict)
    return rt.render("overview.html", page_video=page_video, info_url=info_url, online_url=online_url,
                     type_dict=type_dict, type_desc=type_desc)


@video_view.route("/info/", methods=["POST"])
@login_required
def new_video():
    data = g.request_data
    link_people = data.get("link_people", None)
    r, video_no = c_video.new_video(data["video_name"], data["video_type"], data["video_desc"],
                                    data["episode_num"], data["video_pic"], data["accept_formats"], link_people,
                                    g.user_no)
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
    if g.user_no is None:
        for i in range(len(items) - 1, -1, -1):
            if items[i]["status"] & 64 == 64:
                continue
            del items[i]
    return jsonify({"status": True, "data": items})


@video_view.route("/info/batch/", methods=["POST"])
def batch_get_info_action():
    data = g.request_data
    video_type = data["video_type"]
    multi_no = data["multi_no"]
    items = c_video.select_multi_video(video_type, multi_no)
    if g.user_no is None:
        for i in range(len(items) - 1, -1, -1):
            if items[i]["status"] & 64 == 64:
                continue
            del items[i]
    return jsonify({"status": True, "data": items})


@video_view.route("/info/", methods=["PUT"])
@login_required
def update_video():
    data = g.request_data
    video_type = data["video_type"]
    video_no = data["video_no"]
    l = c_video.update_video(**data)
    return jsonify({"status": True, "data": data})


@video_view.route("/info/", methods=["DELETE"])
@login_required
def delete_video():
    video_no = g.request_data["video_no"]
    video_type = g.request_data["video_type"]
    l = c_video.delete_video(video_type, video_no)
    return jsonify({"status": True, "data": "删除成功"})


@video_view.route("/episode/", methods=["POST", "PUT"])
@login_required
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
    if episode_index > items[0]["episode_num"]:
        return jsonify({"status": False, "data": "视频集索引超出总集数"})
    if request.method == "POST":
        r = True
        l = c_video.new_video_episode(video_type, g.video_no, episode_index, title, episode_url, episode_pic)
    else:
        l = c_video.update_episode(g.video_no, episode_index, title, episode_url, episode_pic)
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
    item = items[0]
    if item["status"] & 1 != 1 and item["upload_num"] != item["episode_num"]:
        return jsonify({"status": False, "data": "视频状态未达到不可上线"})
    c_video.online_video(video_no)
    return jsonify({"status": True, "data": "success"})


@video_view.route("/records/", methods=["POST"])
def record_video_action():
    data = g.request_data
    video_no = g.request_data["video_no"]
    video_type = g.request_data["video_type"]
    episode_index = data["episode_index"]
    c_video.add_record(video_type, video_no, episode_index)
    return jsonify({"status": True, "data": "success"})

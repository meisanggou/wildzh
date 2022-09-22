# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask import request

from flask_helper.template import RenderTemplate
from flask_helper.upload import support_upload2

from wildzh.classes.video import Video
from wildzh.utils.log import getLogger
from wildzh.web02.view import View2

from zh_config import file_prefix_url
from zh_config import upload_folder


__author__ = 'zhouhenglc'


LOG = getLogger()
url_prefix = "/video"

menu_list = {"title": u"视频管理", "icon_class": "icon-shipin",
             "menu_id": "video",
             "sub_menu": [
                 {"title": u"视频管理", "url": url_prefix + "/page"},
                 {"title": u"上传视频", "url": url_prefix + "/upload"},
]}
upload_url = url_prefix + "/upload/"
obj_url = url_prefix + '/obj'
defined_routes = dict(upload_url=upload_url, obj_url=obj_url)
rt = RenderTemplate("exam", menu_active="video",
                    defined_routes=defined_routes)

video_view = View2('video', __name__, url_prefix=url_prefix,
                   auth_required=True, menu_list=menu_list)
video_man = Video()

support_upload2(video_view, upload_folder, file_prefix_url,
                ("exam", "video"), "upload", rename_mode="sha1")


@video_view.route('/page', methods=['GET'])
def video_page():
    return rt.render('video_overview.html', page_title=u'视频管理')


@video_view.route('/upload', methods=['GET'])
def video_upload_page():
    return rt.render('video.html', page_title=u'上传')


@video_view.route('/obj', methods=['POST'])
def add_video():
    data = request.json
    video_title = data['video_title']
    video_desc = data['video_desc']
    video_url = data['video_url']
    video_state = data['video_state']
    obj = video_man.new(g.session, video_title, video_desc, video_state,
                        video_url, g.user_no)
    return obj.to_dict()

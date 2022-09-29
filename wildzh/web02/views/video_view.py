# !/usr/bin/env python
# coding: utf-8
from flask import g
from flask import request

from flask_helper.template import RenderTemplate
from flask_helper.upload import support_upload2
from flask_helper.utils import registry as f_registry

from wildzh.classes.video import Video
from wildzh.classes.video import VideoExamMap
from wildzh.utils import constants
from wildzh.utils.log import getLogger
from wildzh.web02.view import View2

from zh_config import file_prefix_url
from zh_config import upload_folder


__author__ = 'zhouhenglc'


LOG = getLogger()
url_prefix = "/video"

menu_list = {"title": "视频管理", "icon_class": "icon-shipin",
             "menu_id": "video",
             "sub_menu": [
                 {"title": "视频管理", "url": url_prefix + "/page"},
                 {"title": "上传视频", "url": url_prefix + "/upload"},
                 {"title": "关联视频", "url": url_prefix + "/map/page"},
]}
upload_url = url_prefix + "/upload/"
obj_url = url_prefix + '/entries'
map_url = url_prefix + '/map'
defined_routes = dict(upload_url=upload_url, obj_url=obj_url, map_url=map_url)
rt = RenderTemplate("exam", menu_active="video",
                    defined_routes=defined_routes)

video_view = View2('video', __name__, url_prefix=url_prefix,
                   auth_required=True, menu_list=menu_list)
video_man = Video()
video_map_man = VideoExamMap()

support_upload2(video_view, upload_folder, file_prefix_url,
                ("exam", "video"), "upload", rename_mode="sha1")


@video_view.route('/page', methods=['GET'])
def video_page():
    return rt.render('video_overview.html', page_title='视频管理')


@video_view.route('/upload', methods=['GET'])
def video_upload_page():
    return rt.render('video.html', page_title='上传视频')


@video_view.route('/entries', methods=['POST'])
def add_video():
    data = request.json
    video_title = data['video_title']
    video_desc = data['video_desc']
    video_url = data['video_url']
    video_state = data['video_state']
    obj = video_man.new(g.session, video_title, video_desc, video_state,
                        video_url, g.user_no)
    return obj.to_dict()


@video_view.route('/entries', methods=['GET'])
def get_videos():
    items = video_man.get_all(g.session, uploader=g.user_no)
    videos = [item.to_dict() for item in items]

    return {'status': True, 'data': videos}


@video_view.route('/map/page', methods=['GET'])
def set_map_page():
    if 'exam_info_url' not in defined_routes:
        defined_routes['exam_info_url'] = f_registry.DATA_REGISTRY.get(
            constants.DR_KEY_ROUTES)['exam_info_url']
    return rt.render('video_map.html', page_title='关联视频')


@video_view.route('/map', methods=['GET'])
def get_map():
    data = request.args
    filters = {}
    # TODO 必须是管理的题库 或者 必须是自己的视频
    if 'exam_no' in data:
        filters['exam_no'] = data['exam_no']
    if 'video_uuid' in data:
        filters['video_uuid'] = data['video_uuid']
    if not filters:
        return {'status': False, 'data': '请设置题库编号或者视频ID'}
    items = video_map_man.get_all(g.session, **filters)
    data = [item.to_dict() for item in items]
    return {'status': True, 'data': data}


@video_view.route('/map', methods=['POST'])
def set_map():
    data = request.json
    # 必须是管理的题库
    exam_no = data['exam_no']
    # 必须是自己的视频
    video_uuid = data['video_uuid']

    video_subject = data.get('video_subject', None)
    video_chapter = data.get('video_chapter', None)
    position = data.get('position', 0)
    item = video_map_man.new(g.session, exam_no, video_uuid, position,
                             video_subject, video_chapter)
    return {'status': True}


@video_view.route('/map', methods=['UPDATE'])
def update_map():
    data = request.json
    # 必须是管理的题库
    exam_no = data['exam_no']
    video_uuid = data['video_uuid']


@video_view.route('/map', methods=['DELETE'])
def delete_map():
    data = request.json
    # 必须是管理的题库
    exam_no = data['exam_no']
    video_uuid = data['video_uuid']

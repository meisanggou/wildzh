# !/usr/bin/env python
# coding: utf-8
from flask_helper.template import RenderTemplate

from wildzh.utils.log import getLogger
from wildzh.web02.view import View2

__author__ = 'zhouhenglc'


LOG = getLogger()
url_prefix = "/video"

menu_list = {"title": u"视频管理", "icon_class": "icon-shipin",
             "menu_id": "video",
             "sub_menu": [
                 {"title": u"视频管理", "url": url_prefix + "/page"},
                 {"title": u"上传视频", "url": url_prefix + "/page"},
]}

rt = RenderTemplate("exam", menu_active="video")

video_view = View2('video', __name__, url_prefix=url_prefix,
                   auth_required=True, menu_list=menu_list)


@video_view.route('/page', methods=['GET'])
def exam_ad_page():
    return rt.render('video.html', page_title=u'视频管理')

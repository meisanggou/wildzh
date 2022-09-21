# !/usr/bin/env python
# coding: utf-8
from flask_helper.template import RenderTemplate
from flask_helper.upload import support_upload2

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
                 {"title": u"上传视频", "url": url_prefix + "/page"},
]}
upload_url = url_prefix + "/upload/"
defined_routes = dict(upload_url=upload_url)
rt = RenderTemplate("exam", menu_active="video",
                    defined_routes=defined_routes)

video_view = View2('video', __name__, url_prefix=url_prefix,
                   auth_required=True, menu_list=menu_list)


support_upload2(video_view, upload_folder, file_prefix_url,
                ("exam", "video"), "upload", rename_mode="sha1")


@video_view.route('/page', methods=['GET'])
def exam_ad_page():
    return rt.render('video.html', page_title=u'视频管理')

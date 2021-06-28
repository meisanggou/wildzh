# !/usr/bin/env python
# coding: utf-8
from zh_config import db_conf_path

from flask import g
from flask import jsonify
from flask_helper.template import RenderTemplate
from flask_helper.upload import support_upload2
from wildzh.utils.log import getLogger
from wildzh.utils.rich_text import separate_image

from wildzh.classes.exam_ad import ExamAD

from wildzh.web02.view import View2
from wildzh.web02.views.exam_view import required_exam_no
from wildzh.web02.views.exam_view import required_manager_exam

from zh_config import upload_folder, file_prefix_url


__author__ = 'zhouhenglc'

LOG = getLogger()
url_prefix = "/exam/ad"
upload_url = url_prefix + "/upload/"
defined_routes = dict(info_url='/exam/info/', data_url=url_prefix,
                      upload_url=upload_url)
menu = {'menu_id': 'exam', 'is_child': True,
        'sub_menu': [{"title": u"题库推广", "url": url_prefix + "/page"} ]}
exam_ad_view = View2("exam_ad", __name__, url_prefix=url_prefix,
                     auth_required=True,
                     menu_list=menu)
AD_MAN = ExamAD(db_conf_path=db_conf_path)
rt = RenderTemplate("exam", menu_active="exam", defined_routes=defined_routes)


support_upload2(exam_ad_view, upload_folder, file_prefix_url, ("exam", "ad"), "upload",
                rename_mode="sha1")


@exam_ad_view.route('', methods=['GET'])
@required_exam_no
def get_exam_ad():
    data = AD_MAN.select(g.exam_no)
    data['ad_desc_rich'] = separate_image(data['ad_desc'])
    return jsonify({'status': True, 'data': data})


@exam_ad_view.route('/page', methods=['GET'])
def exam_ad_page():
    return rt.render('ad.html', page_title=u'推广信息')


@exam_ad_view.route('', methods=['PUT'])
@required_manager_exam()
def update_exam_ad():
    data = g.request_data
    data['enabled'] = True if data['enabled'] else False
    AD_MAN.update_ad(**data)
    return {'status': True, 'data': data}

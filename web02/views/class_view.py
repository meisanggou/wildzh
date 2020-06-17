# !/usr/bin/env python
# coding: utf-8

from flask_helper import RenderTemplate
from web02 import create_blue

__author__ = 'meisa'

url_prefix = "/classes"

rt = RenderTemplate("classes", menu_active="classes", page_title=u"班级管理")
menu_list = {"title": u"班级管理", "icon_class": "icon-classes", "menu_id": "classes", "sub_menu": [
    {"title": u"我的班级", "url": url_prefix + "/"},
    {"title": u"成员管理", "url": url_prefix + "/"},
    {"title": u"班级资源", "url": url_prefix + "/"},
    {"title": u"创建班级", "url": url_prefix + "/"}
]}

classes_view = create_blue("classes", url_prefix=url_prefix, auth_required=False, menu_list=menu_list)


@classes_view.route("/", methods=["GET"])
def classes_index_page():
    return rt.render("mine.html")
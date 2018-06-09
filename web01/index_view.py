# !/usr/bin/env python
# coding: utf-8
from flask import jsonify, redirect
from flask_helper import RenderTemplate
from web01 import create_blue

__author__ = 'meisa'

rt = RenderTemplate()
index_view = create_blue("index", url_prefix="/")


@index_view.route("/", methods=["GET"])
def index():
    return redirect("/index/")
    return rt.render("index.html")


@index_view.route("/index/", methods=["GET"])
def index2_page():
    m_xl = [u"心理科普", u"心理测试", u"心理调适", u"心理咨询", u"心理电台"]
    m_gx = [u"视频", u"音频"]
    m_jt = [u"视频", u"音频"]
    menu = [m_xl, m_gx, m_jt]
    return rt.render("index2.html")

@index_view.route("/menu/", methods=["GET"])
def get_menu_action():
    m_xl = {"title": u"心理健康", "sub": [
        {"title": u"心理科普", "url": "/article/"},
        {"title": u"心理测试", "url": "/exam/"},
        {"title": u"心理调适", "sub": [
            {"title": u"美文", "url": "/article/"},
            {"title": u"动漫", "url": "/video/"},
            {"title": u"影视", "url": "/video/"},
            {"title": u"音乐", "url": "/music/"}
        ]},
        {"title": u"心理咨询", "url": "/people/"},
        {"title": u"心理电台", "url": "/music/"}]}
    m_gx = {"title": u"国学教育", "sub": [
        {"title": u"视频", "url": "/video/"},
        {"title": u"音频"}]}
    m_jt = {"title": u"家庭教育", "sub": [
        {"title": u"视频", "url": "/video/"},
        {"title": u"音频", "url": "/video/"}]}
    menu = [m_xl, m_gx, m_jt]
    return jsonify({"status": True, "data": menu})

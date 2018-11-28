# !/usr/bin/env python
# coding: utf-8
from flask import jsonify, redirect
from flask_helper import RenderTemplate
from web02 import create_blue

__author__ = 'meisa'

rt = RenderTemplate()
index_view = create_blue("index", url_prefix="/")


@index_view.route("/", methods=["GET"])
def index():
    return redirect("/exam/")


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
        {"title": u"心理科普", "url": "/article/?version=2&article_type=xlts"},
        {"title": u"心理测试", "url": "/exam/?version=2"},
        {"title": u"心理调适", "sub": [
            {"title": u"美文", "url": "/article/?version=2&article_type=meiwen"},
            {"title": u"动漫", "url": "/video/?version=2&video_type=dongman"},
            {"title": u"影视", "url": "/video/?version=2&video_type=yingshi"},
            {"title": u"音乐", "url": "/music/"}
        ]},
        {"title": u"心理咨询", "url": "/people/?version=2&group_id=doctor"},
        {"title": u"心理电台", "url": "/music/"}]}
    m_gx = {"title": u"国学教育", "sub": [
        {"title": u"视频", "url": "/video/?version=2&video_type=gxshipin"},
        {"title": u"音频", "url": "/video/?version=2&video_type=gxyinpin"},
        {"title": u"国学教育专家", "url": "/people/?version=2&group_id=gxedu"}
    ]}
    m_jt = {"title": u"家庭教育", "sub": [
        {"title": u"视频", "url": "/video/?version=2&video_type=jtshipin"},
        {"title": u"音频", "url": "/video/?version=2&video_type=jtyinpin"},
        {"title": u"家庭教育专家", "url": "/people/?version=2&group_id=jtedu"}
    ]}
    menu = [m_xl, m_gx, m_jt]
    return jsonify({"status": True, "data": menu})

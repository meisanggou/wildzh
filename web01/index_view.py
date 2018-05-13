# !/usr/bin/env python
# coding: utf-8
from flask_login import current_user
from flask_helper import RenderTemplate
from web01 import create_blue

__author__ = 'meisa'

rt = RenderTemplate()
exam_view = create_blue("index", url_prefix="/")


@exam_view.route("/", methods=["GET"])
def index():
    return rt.render("index.html")
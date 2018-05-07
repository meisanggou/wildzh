# !/usr/bin/env python
# coding: utf-8
from flask import request, jsonify
from tools import RenderTemplate

from web01 import create_blue

__author__ = 'meisa'

url_prefix="/exam"

rt = RenderTemplate("exam")
exam_view = create_blue("exam", url_prefix=url_prefix)


@exam_view.route("/", methods=["GET"])
def index():
    add_url = url_prefix + "/"
    if "exam_no" in request.args:
        overview_class = ""
        question_class = "active"
    else:
        overview_class = "active"
        question_class = ""
    return rt.render("index.html", add_url=add_url, overview_class=overview_class, question_class=question_class)


@exam_view.route("/", methods=["POST"])
def new_exam():
    data = request.json
    print(data)
    return jsonify({"status": True, "data": data})
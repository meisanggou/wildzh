# !/usr/bin/env python
# coding: utf-8

from flask_helper import RenderTemplate
from web01 import create_blue

__author__ = 'meisa'

rt = RenderTemplate("user")
user_view = create_blue("user", url_prefix="/user")


@user_view.route("/login/", methods=["GET"])
def login_page():
    return rt.render("login.html")

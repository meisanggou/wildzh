#! /usr/bin/env python
# coding: utf-8

import os
from time import time
from flask import request, g, jsonify
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, file_prefix_url
from classes.article import ArticleManager
from web01 import create_blue, upload_folder

__author__ = 'ZhouHeng'

url_prefix = "/article"

rt = RenderTemplate("article", url_prefix=url_prefix)
article_view = create_blue('article_view', url_prefix=url_prefix, menu_list={"title": u"文章管理"})
c_article = ArticleManager(db_conf_path)


@article_view.route("/", methods=["GET"])
def add_func():
    article_no = ""
    g.user_name = "zh_test"
    upload_url = url_prefix + "/upload/"
    page_article = url_prefix + "/?action=article"
    page_list = url_prefix + "/"
    if "article_no" in request.args:
        article_no = request.args["article_no"]
    if request.is_xhr is True:
        if len(article_no) != 32:
            return jsonify({"status": False, "data": "无效的编号"})
        exec_r, data = c_article.get_article(article_no, g.user_name)
        return jsonify({"status": exec_r, "data": data})
    if "action" in request.args and request.args["action"] == "look":
        return rt.render("look.html", article_no=article_no, page_article=page_article, page_list=page_list)
    elif "action" in request.args and request.args["action"] == "article":
        return rt.render("add.html", article_no=article_no, page_list=page_list, upload_url=upload_url)
    query_url = url_prefix + "/query/"
    return rt.render("query.html", query_url=query_url, page_article=page_article)


support_upload2(article_view, upload_folder, file_prefix_url, ("article", "pic"), "upload")


@article_view.route("/", methods=["POST"])
def add_article_action():
    g.user_name = "zh_test"
    request_data = request.json
    title = request_data["title"]
    abstract = request_data["abstract"]
    content = request_data["content"]
    article_desc = request_data["article_desc"]
    pic_url = request_data["pic_url"]
    exec_r, data = c_article.new_article(g.user_name, title, abstract, content, article_desc, pic_url)
    return jsonify({"status": exec_r, "data": data})


@article_view.route("/", methods=["PUT"])
def update_article_action():
    request_data = request.json
    article_no = request_data["article_no"]
    title = request_data["title"]
    abstract = request_data["abstract"]
    content = request_data["content"]
    article_desc = request_data["article_desc"]
    pic_url = request_data["pic_url"]
    auto = request_data.get("auto", False)
    if auto is False:
        exec_r, data = c_article.update_article(article_no, title, abstract, content, article_desc, pic_url)
    else:
        article_file = os.path.join(upload_folder, "%s_%s.txt" % (article_no, int(time())))
        with open(article_file, "w") as wa:
            wa.write(content.encode("utf-8"))
        exec_r, data = True, article_file
    return jsonify({"status": exec_r, "data": data})


@article_view.route("/query/", methods=["GET"])
def query_func():
    if request.is_xhr is True:
        exec_r, articles = c_article.query_article()
        return jsonify({"status": exec_r, "data": articles})
    url_add_article = url_prefix + "/"
    return rt.render("query.html", url_add_article=url_add_article)

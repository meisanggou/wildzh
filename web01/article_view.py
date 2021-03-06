#! /usr/bin/env python
# coding: utf-8

import os
from time import time
from flask import request, g, jsonify
from flask_login import login_required
from flask_helper import RenderTemplate, support_upload2
from zh_config import db_conf_path, file_prefix_url
from classes.article import ArticleManager
from web01 import create_blue, upload_folder

__author__ = 'ZhouHeng'

url_prefix = "/article"

rt = RenderTemplate("article", url_prefix=url_prefix)
article_view = create_blue('article_view', url_prefix=url_prefix, menu_list={"title": u"文章管理"},
                           auth_required=False)
c_article = ArticleManager(db_conf_path)

article_dict = dict(xlts=u"心理调适", meiwen=u"美文")

@article_view.route("/", methods=["GET"])
@login_required
def add_func():
    article_no = ""
    upload_url = url_prefix + "/upload/"
    url_info = url_prefix + "/info/"
    page_article = url_prefix + "/?action=article"
    page_list = url_prefix + "/"
    type_desc = ""
    if "article_type" in request.args and request.args["article_type"] in article_dict:
        article_type = request.args["article_type"]
        type_desc = article_dict[article_type]
        page_article += "&article_type=" + article_type
        page_list += "?article_type=" + article_type
    if "article_no" in request.args:
        article_no = request.args["article_no"]
    if "action" in request.args and request.args["action"] == "look":
        return rt.render("look.html", article_no=article_no, page_article=page_article, page_list=page_list,
                         url_info=url_info, type_desc=type_desc)
    elif "action" in request.args and request.args["action"] == "article":
        return rt.render("add.html", article_no=article_no, page_list=page_list, upload_url=upload_url,
                         url_info=url_info, type_desc=type_desc)
    online_url = url_prefix + "/online/"
    info_url = url_prefix + "/info/"
    return rt.render("query.html", page_article=page_article, online_url=online_url, info_url=info_url,
                     type_desc=type_desc)


support_upload2(article_view, upload_folder, file_prefix_url, ("article", "pic"), "upload")


@article_view.route("/", methods=["POST"])
@login_required
def add_article_action():
    request_data = request.json
    article_type = request_data["article_type"]
    title = request_data["title"]
    author = request_data["author"]
    abstract = request_data["abstract"]
    content = request_data["content"]
    article_desc = request_data["article_desc"]
    pic_url = request_data["pic_url"]
    exec_r, data = c_article.new_article(article_type, author, title, abstract, content, g.user_no, article_desc,
                                         pic_url)
    return jsonify({"status": exec_r, "data": data})


@article_view.route("/", methods=["PUT"])
def update_article_action():
    request_data = request.json
    article_type = request_data["article_type"]
    article_no = request_data["article_no"]
    author = request_data["author"]
    title = request_data["title"]
    abstract = request_data["abstract"]
    content = request_data["content"]
    article_desc = request_data["article_desc"]
    pic_url = request_data["pic_url"]
    auto = request_data.get("auto", False)
    if auto is False:
        exec_r, data = c_article.update_article(article_type, article_no, author, title, abstract, content,
                                                article_desc, pic_url)
    else:
        article_file = os.path.join(upload_folder, "%s_%s.txt" % (article_no, int(time())))
        with open(article_file, "w") as wa:
            wa.write(content.encode("utf-8"))
        exec_r, data = True, article_file
    return jsonify({"status": exec_r, "data": data})


@article_view.route("/info/", methods=["GET"])
def query_func():
    if request.is_xhr is True or g.user_no is None:
        article_type = None
        if "article_type" in request.args:
            article_type = request.args["article_type"]
        if "article_no" in request.args:
            article_no = request.args["article_no"]
            if len(article_no) != 32:
                return jsonify({"status": False, "data": "无效的编号"})
            exec_r, data = c_article.get_article(article_type, article_no, g.user_no)
            if exec_r is True:
                data.update(c_article.get_statistics(article_no))
            return jsonify({"status": exec_r, "data": data})
        exec_r, items = c_article.query_article(article_type=article_type)
        if g.user_no is None:
            for i in range(len(items) - 1, -1, -1):
                if items[i]["status"] & 64 == 64:
                    continue
                del items[i]
        return jsonify({"status": exec_r, "data": items})
    url_add_article = url_prefix + "/"
    return rt.render("query.html", url_add_article=url_add_article)


@article_view.route("/online/", methods=["POST"])
def online_music():
    article_no = g.request_data["article_no"]
    article_type = g.request_data["article_type"]
    r, items = c_article.query_article(article_no=article_no, article_type=article_type)
    if r is False or len(items) != 1:
        return jsonify({"status": False, "data": "文章不存在"})
    c_article.online(article_type, article_no)
    return jsonify({"status": True, "data": "success"})


@article_view.route("/info/", methods=["DELETE"])
def delete_article_action():
    request_data = request.json
    c_article.delete_article(request_data["article_type"], request_data["article_no"])
    return jsonify({"status": True, "data": request_data})
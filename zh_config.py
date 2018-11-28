# !/usr/bin/env python
# coding: utf-8

import os

__author__ = 'meisa'

script_dir = os.path.abspath(os.path.dirname(__file__))


web_pro = "01"

c_static_prefix_url = "/static00"
static_prefix_url = "/static01"
file_prefix_url = "/file"

db_conf_path = os.path.join(script_dir, "mysql_app.conf")
min_program_conf = os.path.join(script_dir, "mini_program.conf")

# 目录相关配置
upload_folder = os.environ.get("ZH_UPLOAD_FOLDER", "W:\\zhupload")


accept_agent = "firefox|chrome|safari|window|GitHub|jyrequests|micro|Aliyun"

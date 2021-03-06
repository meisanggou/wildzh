# !/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])


from web02 import app, portal_menu_list

__author__ = 'meisa'

app_dir = os.path.split(os.path.abspath(__file__))[0]
view_files = os.listdir(os.path.join(app_dir))
for view_file in view_files:
    if view_file.endswith("_view.py"):
        __import__("web02.%s" % view_file[:-3])

app.register_blues()
l_menu = len(portal_menu_list) + 10
for item in portal_menu_list:
    if item["index"] < 0:
        item["index"] += l_menu * 2
portal_menu_list.sort(key=lambda x: x["index"])
app.jinja_env.globals["portal_menu_list"] = portal_menu_list

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2400)
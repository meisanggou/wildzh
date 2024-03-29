# !/usr/bin/env python
# coding: utf-8

import os
import sys
from flask_helper.utils.registry import DataRegistry

from wildzh.web02 import app
from wildzh.utils.log import getLogger

__author__ = 'meisa'

LOG = getLogger()
portal_menu_list = DataRegistry.get_instance().get('portal_menu_list', [])
l_menu = len(portal_menu_list) + 10
for item in portal_menu_list:
    if item["index"] < 0:
        item["index"] += l_menu * 2
portal_menu_list.sort(key=lambda x: x["index"])
app.jinja_env.globals["portal_menu_list"] = portal_menu_list

if __name__ == "__main__":
    port = 2400
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host="0.0.0.0", port=port, log=LOG)

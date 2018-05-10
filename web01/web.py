# !/usr/bin/env python
# coding: utf-8

import os
import sys
# sys.path.append(os.path.split(os.path.dirname(__file__))[0])


from web01 import app

__author__ = 'meisa'

app_dir = os.path.split(os.path.abspath(__file__))[0]
view_files = os.listdir(os.path.join(app_dir))
for view_file in view_files:
    if view_file.endswith("_view.py"):
        __import__("web01.%s" % view_file[:-3])

app.register_blues()

if __name__ == "__main__":
    app.run(port=2400)
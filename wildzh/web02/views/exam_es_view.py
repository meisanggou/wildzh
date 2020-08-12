# !/usr/bin/env python
# coding: utf-8
from flask import request
from wildzh.utils.async_pool import get_pool
from wildzh.utils.log import getLogger
from wildzh.web02.view import View2

__author__ = 'zhouhenglc'

LOG = getLogger()
url_prefix = "/exam/es"

# exam_es_view = View2("exam", __name__, url_prefix=url_prefix)

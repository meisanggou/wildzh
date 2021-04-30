# !/usr/bin/env python
# coding: utf-8
from werkzeug.exceptions import HTTPException

__author__ = 'zhouhenglc'


class BadRequest(HTTPException):
    code = 400

#! /usr/bin/env python
# coding: utf-8

import time

from zh_config import web_pro, static_prefix_url, c_static_prefix_url
from wildzh.tools.ip_man import IPManager

ip = IPManager()

__author__ = 'ZhouHeng'


def unix_timestamp(t, style="time"):
    if isinstance(t, (int, float)):
        x = time.localtime(t)
        if style == "time":
            return time.strftime('%H:%M:%S', x)
        elif style == "month":
            return time.strftime('%Y%m', x)
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", x)
    return t


def bit_and(num1, num2):
    return num1 & num2


def ip_str(ip_v):
    if type(ip_v) == int:
        return ip.ip_value_str(ip_value=ip_v)
    return ip_v


def _make_static_url(static_url, filename):
    return static_url + "/" + filename


def make_static_url(filename):
    return _make_static_url(static_prefix_url, filename)


def make_default_static_url(filename):
    return "/static" + web_pro + "/" + filename


def _make_static_html(filename, static_url):
    if filename.startswith("http"):
        src = filename
        default_src = filename
    else:
        src = _make_static_url(static_url, filename)
        default_src = make_default_static_url(filename)
    if filename.endswith(".js"):
        html_s = "<script type=\"text/javascript\" src=\"%s\" onerror=\"this.src='%s'\"></script>" % (src, default_src)
    else:
        html_s = "<link rel=\"stylesheet\" href=\"%s\" onerror=\"this.href='%s'\">" % (src, default_src)
    return html_s


def make_static_html(filename):
    return _make_static_html(filename, static_prefix_url)


def make_static_html2(filename):
    return _make_static_html(filename, c_static_prefix_url)


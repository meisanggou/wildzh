# !/usr/bin/env python
# coding: utf-8
from zh_config import db_conf_path

from flask import g
from flask import jsonify
from flask import request
from wildzh.utils.log import getLogger

from wildzh.classes.exam_ad import ExamAD

from wildzh.web02.view import View2


__author__ = 'zhouhenglc'

LOG = getLogger()

url_prefix = '/wx'
wx_view = View2("wx", __name__, url_prefix=url_prefix)

# 微信主动调用方法
@wx_view.route("/token", methods=["GET"])
def check_signature():
    try:
        signature = request.args["signature"]
        timestamp = request.args["timestamp"]
        nonce = request.args["nonce"]
        echostr = request.args["echostr"]
        if wx.check_signature(signature, timestamp, nonce):
            return echostr
        return "false"
    except Exception as e:
        print(e.args)
        return "false"


# 微信主动调用方法
@wx_view.route("/token", methods=["POST"])
def get_wx_msg():
    try:
        request_data = request.data
        read_request = open("wx_request.log", "a")
        read_request.write(request.url + "\n")
        read_request.write(str(request.headers) + "\n")
        read_request.write(request_data + "\n")
        read_request.write(request.remote_addr + "\n")
        read_request.close()
        # 判断请求IP是否是微信服务器IP
        if wx.check_wx_ip(g.request_IP_s) is False:
            return ""
        signature = request.args["signature"]
        timestamp = request.args["timestamp"]
        nonce = request.args["nonce"]
        msg_signature = None
        if "encrypt_type" in request.args:
            if request.args["encrypt_type"] == "aes":
                msg_signature = request.args["msg_signature"]
        request_data = request.data
        return wx.handle_msg(request_data, signature, timestamp, nonce, msg_signature)
    except Exception as e:
        print(e.args)
        return ""

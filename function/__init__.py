# !/usr/bin/env python
# coding: utf-8

import os
import qrcode
from PIL import Image
from web_func import unix_timestamp, make_static_html, make_default_static_url
from web_func import make_static_url, make_static_html2

__author__ = 'meisa'


def generate_qr(content, save_path, paste_img_path=None):
    qr = qrcode.QRCode(version=2, box_size=10, border=2)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image()
    img = img.convert("RGBA")
    if paste_img_path is not None and os.path.exists(paste_img_path) is True:
        icon = Image.open(paste_img_path)
        img_w, img_h = img.size
        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)

        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)

        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        img.paste(icon, (w, h))

    img.save(save_path)


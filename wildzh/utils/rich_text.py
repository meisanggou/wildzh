# !/usr/bin/env python
# coding: utf-8
import re

__author__ = 'zhouhenglc'


def separate_image(text, max_width=None):
    text_groups = []
    s_l = re.findall(r"(\[\[([/\w.]+?):([\d.]+?):([\d.]+?)\]\])", text)
    last_point = 0
    index = 0
    for items in s_l:
        item = items[0]
        point = text[last_point:].index(item)
        prefix_s = text[last_point: last_point + point]
        if len(prefix_s) > 0:
            text_groups.append({'value': prefix_s, 'index': index})
            index += 1
        o_item = dict(value=item, url=items[1], width=float(items[2]), height=float(items[3]))
        if max_width and max_width < o_item["width"]:
            o_item["height"] = o_item["height"] * max_width / o_item["width"]
            o_item["width"] = max_width
        o_item['index'] = index
        index += 1
        text_groups.append(o_item)
        last_point = last_point + point + len(item)
    if last_point < len(text):
        text_groups.append({'value': text[last_point:], 'index': index})
    return text_groups

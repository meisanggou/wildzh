# !/usr/bin/env python
# coding: utf-8
import re

__author__ = 'zhouhenglc'


def _split_wrap(item):
    _items = item.split('\n')
    _l = [_items[0]]
    for i in range(1, len(_items)):
        _l.append('\n')
        _l.append(_items[i])
    return _l

def separate_image(text, max_width=None, host=None):
    text_groups = []
    s_l = re.findall(r"(\[\[([/\w.]+?):([\d.]+?):([\d.]+?)\]\])", text)
    last_point = 0
    index = 0
    for items in s_l:
        item = items[0]
        point = text[last_point:].index(item)
        prefix_s = text[last_point: last_point + point]
        if len(prefix_s) > 0:
            for _item in _split_wrap(prefix_s):
                text_groups.append({'value': _item, 'index': index})
                index += 1
        o_item = dict(value=item, url=items[1], width=float(items[2]),
                      height=float(items[3]))
        # if host:
        #     o_item['href'] = host + o_item['url']
        if max_width and max_width < o_item["width"]:
            o_item["height"] = o_item["height"] * max_width / o_item["width"]
            o_item["width"] = max_width
        # o_item['style'] = "height:%spx;width:%spx" % (o_item["height"],
        #                                               o_item["width"])
        o_item['index'] = index
        index += 1
        text_groups.append(o_item)
        last_point = last_point + point + len(item)
    if last_point < len(text):
        for _item in _split_wrap(text[last_point:]):
            text_groups.append({'value': _item, 'index': index})
            index += 1
    return text_groups

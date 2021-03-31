# !/usr/bin/env python
# coding: utf-8
import os

from wildzh.utils import constants

__author__ = 'zhouhenglc'

script_file = os.path.join(__file__)
TEXT_DIR = os.path.abspath(os.path.join(os.path.dirname(script_file), '..',
                                        'text'))

def load_text(name):
    if not name.endswith('txt'):
        name = '%s.txt' % name
    path = os.path.join(TEXT_DIR, name)
    with open(path, encoding=constants.ENCODING) as r:
        c = r.read()
        return c


def convert_to_list(text):
    lines = text.split('\n')
    sections = []
    items = []
    title = ""
    for line in lines:
        if not line:
            continue
        if line[0] == '[' and line[-1] == ']':
            if title:
                sections.append({'title': title, 'items': items})
            title = line[1:-1]
            items = []
        else:
            items.append(line)
    if title:
        sections.append({'title': title, 'items': items})
    return sections

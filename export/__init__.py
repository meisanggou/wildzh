# !/usr/bin/env python
# coding: utf-8
import json
import os
import Queue
import re
import zipfile

import jinja2

__author__ = 'zhouhenglc'


abs_dir = os.path.abspath(os.path.dirname(__file__))


def get_num(s):
    return 100 + int("".join(re.findall("\d", s)))


def get_menu_name(s):
    s = "".join(re.split(" ", s))
    return s + " " * (18 - len(s) * 2)

text_run_template = u"""<w:r>
  <w:rPr>
    <w:rFonts w:ascii="宋体" w:eastAsia="宋体" w:hAnsi="宋体" w:cs="宋体" w:hint="eastAsia"/>
    <w:sz w:val="24"/>
  </w:rPr>
  <w:t>%(text)s</w:t>
</w:r>
"""

image_run_template = None


def load_run_template():
    global image_run_template
    demo_path = os.path.join(abs_dir, 'image_demo.xml')
    if image_run_template is None:
        with open(demo_path) as ri:
            image_run_template = ri.read()
    return image_run_template


def transfer(s):
    _d = ["&", "&amp;", "<", "&lt;", ">", "&gt;", "'", "&apos;", '"', '&quot;']
    for i in range(0, len(_d), 2):
        s = s.replace(_d[i], _d[i + 1])
    return s


def convert_run_xml(s):
    if isinstance(s, dict):
        if 'r_index' in s:
            ts = load_run_template() % s
        else:
            ts = transfer(json.dumps(s))
    else:
        ts = transfer(s)
    # print(ts)
    return text_run_template % {'text': ts}


def write_zip(target_dir, target_files=None):
    abs_target_dir = os.path.abspath(target_dir)
    all_files = []
    q = Queue.Queue()
    if target_files is None:
        q.put(abs_target_dir)
    else:
        for item in target_files:
            abs_item = os.path.abspath(os.path.join(abs_target_dir, item))
            q.put(abs_item)
    while q.empty() is False:
        p = q.get()
        if os.path.isdir(p) is True:
            for item in os.listdir(p):
                abs_item = os.path.abspath(os.path.join(p, item))
                q.put(abs_item)
        else:
            all_files.append(p)
    relative_files = []
    target_len = len(abs_target_dir) + 1
    for item in all_files:
        relative_files.append([item, item[target_len:]])
    return relative_files


def packet_zip(filename, demo_dir):
    zip_write = zipfile.ZipFile(filename, "w")
    zip_files = write_zip(demo_dir, ["_rels", "docProps", "word", "[Content_Types].xml"])
    for z_file in zip_files:
        zip_write.write(z_file[0], z_file[1])
    zip_write.close()


def write_xml(filename, demo_dir, **kwargs):
    medias = kwargs.pop('medias', [])
    doc_file = os.path.join(demo_dir, 'word/document.xml')
    rels_file = os.path.join(demo_dir, 'word/_rels/document.xml.rels')

    env = jinja2.Environment()
    env.filters["transfer"] = transfer
    env.filters["get_num"] = get_num
    env.filters["get_menu_name"] = get_menu_name
    env.filters['convert_run_xml'] = convert_run_xml
    template_str = open("document_demo2.xml").read().decode("utf-8")
    t = env.from_string(template_str)
    r = t.render(**kwargs)

    with open(doc_file, "w") as w:
        w.write(r.encode("utf-8"))
    if medias:
        m_ts = open('rels_demo.xml').read().decode('utf-8')
        mt = env.from_string(m_ts)
        mr = mt.render(medias=medias)
        with open(rels_file, 'w') as wm:
            wm.write(mr.encode('utf-8'))

    packet_zip(filename, demo_dir)
    # clear file
    os.remove(doc_file)
    os.remove(rels_file)
    media_dir = os.path.join(demo_dir, 'word/media')
    exist_mf = os.listdir(media_dir)
    for item in exist_mf:
        _file = os.path.join(media_dir, item)
        os.remove(_file)
    return filename

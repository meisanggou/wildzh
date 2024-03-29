# !/usr/bin/env python
# coding: utf-8
import jinja2
import json
import os
import re
from wildzh.utils import constants
from wildzh.export.xml2docx import directory_to_docx

__author__ = 'zhouhenglc'


abs_dir = os.path.abspath(os.path.dirname(__file__))


def get_num(s):
    return 100 + int("".join(re.findall("\d", s)))


def get_menu_name(s):
    s = "".join(re.split(" ", s))
    return s + " " * (18 - len(s) * 2)


text_run_template = u"""
<w:r>
  <w:rPr>
    <w:rFonts w:ascii="宋体" w:eastAsia="宋体" w:hAnsi="宋体" w:cs="宋体" w:hint="eastAsia"/>
    <w:sz w:val="24"/>
  </w:rPr>
  <w:t>%(text)s</w:t>
</w:r>
"""
table_tr_tc_template = """<w:tc>
    <w:tcPr>
        <w:tcW w:w="%(w)s" w:type="dxa"/>
    </w:tcPr>
    <w:p w:rsidR="00550B8B" w:rsidRDefault="00550B8B" w:rsidP="003F6934">
        <w:pPr>
            <w:rPr>
                <w:rFonts w:ascii="宋体" w:eastAsia="宋体" w:hAnsi="宋体" w:cs="宋体"/>
                <w:sz w:val="24"/>
            </w:rPr>
        </w:pPr>
        %(text_xml)s
    </w:p>
</w:tc>
"""

image_run_template = None


def load_run_template():
    global image_run_template
    demo_path = os.path.join(abs_dir, 'image_demo3.xml')
    if image_run_template is None:
        with open(demo_path, encoding=constants.ENCODING) as ri:
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
            return ts
        else:
            ts = transfer(json.dumps(s))
    else:
        ts = transfer(s)
    # print(ts)
    return text_run_template % {'text': ts}


def convert_table_tr_tc_xml(rs, w=2130):
    rs_xml = []
    for s in rs:
        rs_xml.append(convert_run_xml(s))
    text_xml = '\n'.join(rs_xml)
    return table_tr_tc_template % {'text_xml': text_xml, 'w': w}


def convert_table_tr_tc4_xml(rs):
    # 每行有4列
    return convert_table_tr_tc_xml(rs, 2130)


def convert_table_tr_tc2_xml(rs):
    # 每行有2列
    return convert_table_tr_tc_xml(rs, 4261)


def write_xml(filename, demo_dir, **kwargs):
    medias = kwargs.pop('medias', [])
    answer_medias = kwargs.pop('answer_medias', [])
    show_answer = kwargs.get('show_answer', False)
    if show_answer or kwargs.get('alone_answers'):
        medias += answer_medias
    doc_file = os.path.join(demo_dir, 'word/document.xml')
    rels_file = os.path.join(demo_dir, 'word/_rels/document.xml.rels')

    doc_demo2 = os.path.join(abs_dir, "document_demo3.xml")
    rels_demo = os.path.join(abs_dir, 'rels_demo3.xml')

    env = jinja2.Environment()
    env.filters["transfer"] = transfer
    env.filters["get_num"] = get_num
    env.filters["get_menu_name"] = get_menu_name
    env.filters['convert_run_xml'] = convert_run_xml
    env.filters['convert_table_tr_tc4_xml'] = convert_table_tr_tc4_xml
    env.filters['convert_table_tr_tc2_xml'] = convert_table_tr_tc2_xml
    template_str = open(doc_demo2, encoding=constants.ENCODING).read()
    t = env.from_string(template_str)
    r = t.render(**kwargs)

    with open(doc_file, "w", encoding=constants.ENCODING) as w:
        w.write(r)
    if medias:
        m_ts = open(rels_demo, encoding=constants.ENCODING).read()
        mt = env.from_string(m_ts)
        mr = mt.render(medias=medias)
        with open(rels_file, 'w', encoding=constants.ENCODING) as wm:
            wm.write(mr)

    directory_to_docx(filename, demo_dir)
    # clear file
    # os.remove(doc_file)
    if medias:
        os.remove(rels_file)
        if kwargs.pop('clear_demo', False):
            media_dir = os.path.join(demo_dir, 'word/media')
            for m_item in medias:
                _file = os.path.join(media_dir, m_item['name'])
                try:
                    os.remove(_file)
                except Exception as e:
                    pass
    return filename

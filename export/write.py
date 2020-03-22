 # !/usr/bin/env python
# coding: utf-8

import re
import os
import json
import jinja2
import zipfile
import Queue
import requests


__author__ = 'meisa'

SERVER_EP = 'https://wild.gene.ac'
OPTION_MAPPING = ["A", "B", "C", "D"]
cn_num = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一"]
session = requests.session()
session.headers["User-Agent"] = "jyrequests"


text_run_template = u"""<w:r>
  <w:rPr>
    <w:rFonts w:ascii="宋体" w:eastAsia="宋体" w:hAnsi="宋体" w:cs="宋体" w:hint="eastAsia"/>
    <w:sz w:val="24"/>
  </w:rPr>
  <w:t>%(text)s</w:t>
</w:r>
"""
with open('image_demo.xml') as ri:
    image_run_template = ri.read()


def get_num(s):
    return 100 + int("".join(re.findall("\d", s)))


def get_menu_name(s):
    s = "".join(re.split(" ", s))
    return s + " " * (18 - len(s) * 2)


ONE = False


def convert_run_xml(s):
    if isinstance(s, dict):
        if 'r_index' in s:
            ts = image_run_template % s
        else:
            ts = transfer(json.dumps(s))
    else:
        ts = transfer(s)
    # print(ts)
    return text_run_template % {'text': ts}


def transfer(s):
    if isinstance(s, dict):
        print(s)
        return json.dumps(s)
    _d = ["&", "&amp;", "<", "&lt;", ">", "&gt;", "'", "&apos;", '"', '&quot;']
    for i in range(0, len(_d), 2):
        s = s.replace(_d[i], _d[i + 1])
    return s


def string_length(s):
    if isinstance(s, str):
        s = s.decode("utf-8")
    all_ch = re.findall(u"[\u4E00-\u9FA5]+", s)
    plus_len = 0
    for item in all_ch:
        plus_len += len(item)
    return len(s) + plus_len


def login():
    url = "%s/user/login/password/" % SERVER_EP
    response = session.post(url, json=dict(user_name="admin", password="admin", next=""))
    print(response.text)


def request_questions(exam_no, num, select_mode=None):
    params = dict(exam_no=exam_no, num=num)
    if select_mode:
        params['select_mode'] = select_mode
    url = "%s/exam/questions/" % SERVER_EP
    response = session.get(url, params=params)
    return response.json()


def download_file(path, save_dir, name):
    url = '%s%s' % (SERVER_EP, path)
    resp = session.get(url)
    save_path = os.path.join(save_dir, name)
    with open(save_path, 'wb')as wb:
        wb.write(resp.content)
    return save_path


def receive_data(exam_no, media_dir):
    # 登陆
    login()
    # 获取 60道 选择题
    single_selected = request_questions(exam_no, 60, 1)["data"]
    answer_blocks = []
    # 获得 5题 名词解释
    block1 = request_questions(exam_no, 5, 2)["data"]
    answer_blocks.append(dict(title=u"名词解释(每小题3分,共15分)", questions=block1))
    # 获得 4题 简答题
    block2 = request_questions(exam_no, 4, 3)["data"]
    answer_blocks.append(dict(title=u"简答题(每小题5分,共20分)", questions=block2))
    # 获得 2题 计算题
    block3 = request_questions(exam_no, 2, 4)["data"]
    answer_blocks.append(dict(title=u"计算题(70题10分,71题15分,共25分)", questions=block3))
    # 获得 2题 论述题
    block4 = request_questions(exam_no, 2, 5)["data"]
    answer_blocks.append(dict(title=u"论述题(每小题15分,共30分)", questions=block4))

    #  数据处理
    question_no = 1
    rid_i = 100
    rid_p = 'rId'
    medias = []
    for s_item in single_selected:
        for r_item in s_item['question_desc_rich']:
            if isinstance(r_item, dict):
                rid = "%s%s" % (rid_p, rid_i)
                r_item['rid'] = rid
                r_item['width'] = int(r_item['width'] * 10000)
                r_item['height'] = int(r_item['height'] * 10000)
                r_item['r_index'] = rid_i
                r_name = '%s.%s' % (rid, r_item['url'].rsplit('.', 1)[-1])
                r_item['name'] = r_name
                download_file(r_item['url'], media_dir, r_name)
                rid_i += 1
                medias.append({'rid': rid, 'name': r_name})
        s_item["this_question_no"] = question_no
        question_no += 1
        max_score = -100
        right_index = -1
        max_option_len = 0
        for index in range(len(s_item["options"])):
            item = s_item["options"][index]
            o_len = 0
            for dr_item in item['desc_rich']:
                if isinstance(dr_item, dict):
                    o_len = 29
                else:
                    o_len += string_length(dr_item)
            if o_len > max_option_len:
                max_option_len = o_len
            if "score" not in item:
                item["score"] = 0
            if item["score"] > max_score:
                max_score = item["score"]
                right_index = index
        if max_option_len <= 12:
            s_item["option_style"] = "t_four"
        elif max_option_len <= 28:
            s_item["option_style"] = "t_two"
        else:
            s_item["option_style"] = "one"
        s_item["right_option"] = OPTION_MAPPING[right_index]

    for q_block in answer_blocks:
        for q_item in q_block["questions"]:
            q_item["this_question_no"] = question_no
            # q_item["multi_question_desc"] = filter(lambda x: len(x) > 0, q_item["question_desc"].split("\n"))
            q_item["multi_question_desc"] = []
            question_no += 1
    r = {'single_selected': single_selected,
         'answer_blocks': answer_blocks,
         'option_mapping': OPTION_MAPPING,
         'medias': medias}
    return r


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


def packet_zip(filename):
    zip_write = zipfile.ZipFile(filename, "w")
    zip_files = write_zip("demo2", ["_rels", "docProps", "word", "[Content_Types].xml"])
    for z_file in zip_files:
        zip_write.write(z_file[0], z_file[1])
    zip_write.close()


def write_xml(filename, **kwargs):
    medias = kwargs.pop('medias', [])
    env = jinja2.Environment()
    env.filters["transfer"] = transfer
    env.filters["get_num"] = get_num
    env.filters["get_menu_name"] = get_menu_name
    env.filters['convert_run_xml'] = convert_run_xml
    template_str = open("document_demo2.xml").read().decode("utf-8")
    t = env.from_string(template_str)
    r = t.render(**kwargs)
    with open("demo2/word/document.xml", "w") as w:
        w.write(r.encode("utf-8"))
    if medias:
        m_ts = open('rels_demo.xml').read().decode('utf-8')
        mt = env.from_string(m_ts)
        mr = mt.render(medias=medias)
        with open('demo2/word/_rels/document.xml.rels', 'w') as wm:
            wm.write(mr.encode('utf-8'))

    packet_zip(filename)
    return filename


if __name__ == "__main__":
    q_data = receive_data('1570447137', 'demo2/word/media')
    # q_data['single_selected'] = []
    # q_data['answer_blocks'] = []
    write_xml('2.docx', exam_name=u'自测题', show_answer=False, **q_data)

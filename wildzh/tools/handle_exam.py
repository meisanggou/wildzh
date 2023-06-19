# !/usr/bin/env python
# coding: utf-8

import json
import os
import re
import requests
import subprocess
import uuid

from wildzh.tools.parse_question import QuestionSet, AnswerLocation
from wildzh.tools.docx.object import DocxObject
from wildzh.tools.read_xml import handle_answers_docx_main_xml, handle_docx_main_xml
from wildzh.utils import img

__author__ = 'zhouhenglc'

req = requests.session()
headers = {"User-Agent": "jyrequests"}
req.headers = headers

remote_host = "http://127.0.0.1:2400"
remote_host = "https://wild.gene.ac"

exec_file_dir, exec_file_name = os.path.split(os.path.abspath(__file__))
EXE_WMF_TO_PNG = os.path.join(exec_file_dir, "Wmf2Png.exe")

REAL_UPLOAD = False


def execute_cmd(cmd):
    cmd = [str(p) for p in cmd]
    sub_pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # sub_pro.wait()
    s = sub_pro.communicate()
    o_lines = []
    for l in s:
        if isinstance(l, bytes):
            l = l.decode('utf-8').strip()
        o_lines.append(l)
    output = "\n".join(o_lines)
    return sub_pro.returncode, output


def wmf_2_png(wmf_path, width, height, multiple=3):
    cmd = [EXE_WMF_TO_PNG, wmf_path, width, height, str(multiple)]
    code, output = execute_cmd(cmd)
    return output.strip()


def login(server, user_name, password):
    url = server + "/user/login/password/"
    data = dict(user_name=user_name, password=password, next="/exam/")
    response = req.post(url, json=data)
    print(response.text)


def req_max_no(server, exam_no):
    url = server + "/exam/questions/no/"
    response = req.get(url, params=dict(exam_no=exam_no))
    res = response.json()
    if res['status'] is False:
        raise RuntimeError(res['data'])
    print(res)
    return res["data"]


def post_questions(server, questions_set):
    exam_no = questions_set.exam_no
    no_info = req_max_no(server, exam_no)
    print(no_info)
    next_no = no_info["next_no"]
    url = server + "/exam/questions/?exam_no=%s" % exam_no
    question_no = next_no
    print(questions_set.set_source)
    # 正式上传前 必须 先dry_run
    drt_path = '.%s.dry_run' % questions_set.exam_name
    questions_set.ensure_no_math()
    if questions_set.dry_run:
        with open(drt_path, 'w') as w:
            w.write('')
        upload_func  = upload_media_to_server_dummy
    else:
        if not os.path.exists(drt_path):
            raise RuntimeError('Please dry_run first')
        os.remove(drt_path)
        upload_func = upload_media_to_server
    for q_item in questions_set:
        q_item_d = q_item.to_exam_dict(upload_func, server)
        q_item_d["question_no"] = question_no
        if questions_set.set_source:
            q_item_d["question_source"] = questions_set.exam_name
            q_item_d['question_source_no'] = q_item.no
        else:
            q_item_d["question_source"] = ""
        q_item_d["question_subject"] = questions_set.question_subject  # 无
        if questions_set.dry_run:
            print(json.dumps(q_item_d))
        if not questions_set.dry_run:
            resp = req.post(url, json=q_item_d)
            print(resp.text)
        question_no += 1


def set_questions(server, questions_set):
    d_set_keys = ['answer', 'question_desc']
    set_keys = getattr(questions_set, 'set_keys', d_set_keys)
    exam_no = questions_set.exam_no
    url = server + "/exam/questions/?exam_no=%s" % exam_no
    for q_item in questions_set:
        q_item_d = q_item.to_update_dict(*set_keys)
        # if set_source:
        #     q_item_d["question_source"] = question_set.exam_name
        # else:
        #     q_item_d["question_source"] = ""
        if questions_set.dry_run:
            print(q_item_d)
            print(json.dumps(q_item_d))
        if not questions_set.dry_run:
            resp = req.put(url, json=q_item_d)
            print(resp.text)


def replace_media2(text, q_rl):
    """

    :param text:  [[rId49$28$13]]
    :param q_rl:
    :param cache_rl:
    :return:
    """
    media_comp = re.compile(r"(\[\[([a-z0-9]+?)\$([\d.]+?)\$([\d.]+?)(|\$[\d\.\-|]+?)\]\])", re.I)
    found_rs = media_comp.findall(text)
    medias = {}
    for r_item in found_rs:
        r_t = r_item[0]
        m_id = r_item[1]
        width = r_item[2]
        height = r_item[3]
        clip_data = None
        if len(r_item[4]) != 0:
            # 需要裁剪
            left, top, right, bottom = r_item[4][1:].split("|")
            clip_data = [left, top, right, bottom]
            # 需要裁剪
            for i in range(4):
                if clip_data[i] == "":
                    clip_data[i] = 0
                elif clip_data[i].startswith("-"):
                    clip_data[i] = 0
                else:
                    clip_data[i] = float(clip_data[i]) / 1000.0
        m_path = get_media(m_id, q_rl, width, height, clip_data)
        n_point = '[[%s]]' % str(uuid.uuid4())
        text = text.replace(r_t, "[[%s:%s:%s]]" % (n_point, width, height))
        medias[n_point] = m_path
    return text, medias


def upload_media_to_server_dummy(file_path, *args, **kwargs):
    if not os.path.exists(file_path):
        raise RuntimeError('file %s not exist!' % file_path)
    return '/static/dummy'


def upload_media_to_server(file_path, server, freq=0):
    url = server + "/exam/upload/"
    files = dict(pic=open(file_path, "rb"))
    try:
        resp = req.post(url, files=files)
        print('upload %s success' % file_path)
        return resp.json()["data"]["pic"]
    except Exception as e:
        if freq >= 5:
            raise
        freq += 1
        return upload_media_to_server(server, file_path, freq)


def get_media(r_id, rl, width, height, clip_data=None):
    o_pic = rl[r_id]
    o_pic_ext = o_pic.rsplit(".")[-1].lower()
    if o_pic_ext in ("jpeg", "png", "jpg"):
        png_file = o_pic
    else:
        png_file = wmf_2_png(rl[r_id], width, height)
    if clip_data is not None:
        # 需要裁剪
        png_file = img.clip_pic(png_file, clip_data)
    return png_file


def handle_exam_no_answer(file_path, questions_set):
    exam_name = questions_set.exam_name
    print("start handle %s" % exam_name)
    with DocxObject(file_path) as do:
        handle_docx_main_xml(do, ".", u"、", u"．", ':',
                             questions_set=questions_set)
        q_rl = do.relationships
        if questions_set.length <= 0:
            raise RuntimeError("没发现题目")
        for q_item in questions_set:
            q_no = q_item.no
            # 开始上传 题目
            # 获取题目描述中的图片
            q_item.desc = replace_media2(q_item.desc, q_rl)

            # 获取选项中的图片
            for option in q_item.options:
                option.desc = replace_media2(option.desc, q_rl)

            q_item.ensure_has_answer()

            # 获取答案中的图片
            q_item.answer = replace_media2(q_item.answer, q_rl)

        if questions_set.set_mode:
            set_questions(remote_host, questions_set)
        else:
            post_questions(remote_host, questions_set)
    return True, "success"


def handle_exam_with_answer(file_path, questions_set):
    print(file_path)
    exam_name = os.path.basename(file_path).rsplit(".", 1)[0]
    answer_file = None
    if questions_set.answer_location.IAmFile:
        answer_file = file_path.replace(".docx", u"答案.docx")
        if os.path.exists(answer_file) is False:
            msg = ("Ignore %s, not Answer" % file_path)
            print(msg)
            return False, msg
    print("start handle %s" % exam_name)
    with DocxObject(file_path) as do:
        handle_docx_main_xml(do, ".", u"、", u"．", ':',
                             questions_set=questions_set)
        q_rl = do.relationships
        if questions_set.length <= 0:
            raise RuntimeError("没发现题目")
        for q_item in questions_set:
            # 获取题目描述中的图片
            q_item.desc = replace_media2(q_item.desc, q_rl)
            # 获取选项中的图片
            for option in q_item.options:
                option.desc = replace_media2(option.desc, q_rl)
            if not answer_file:
                q_item.ensure_has_answer()
                # 获取答案中的图片
                q_item.answer = replace_media2(q_item.answer, q_rl)
        if answer_file:
            with DocxObject(answer_file) as ado:
                answers_dict = handle_answers_docx_main_xml(ado, questions_set)
                aw_rl = ado.relationships
                for q_item in questions_set:
                    # 判定是否包含答案
                    answer_obj = answers_dict.find_answer(q_item)
                    if not answer_obj:
                        raise RuntimeError("lack answer %s %s" % (
                            q_item.select_mode, q_item.no))
                    q_item.set_answer(answer_obj)
                    # 获取答案中的图片
                    q_item.answer = replace_media2(q_item.answer, aw_rl)
                post_questions(remote_host, questions_set)
        else:
            post_questions(remote_host, questions_set)
    return True, "success"


def handle_exam(file_path, question_set):
    handle_exam_with_answer(file_path, question_set)
    return
    if question_set.answer_location.IAmFile:
        handle_exam_with_answer(file_path, question_set)
    else:
        handle_exam_no_answer(file_path, question_set)


def transfer_exam(s_exam, start_no, end_no, t_exam, select_mode=None,
                  target_start_no=None, random=False):
    url = remote_host + '/exam/transfer'
    data = {'source_exam_no': s_exam, 'start_no': start_no,
            'end_no': end_no, 'target_exam_no': t_exam}
    if select_mode:
        data['select_mode'] = select_mode
    if target_start_no is not None:
        data['target_start_no'] = target_start_no
    if random:
        data['random'] = True
    response = req.post(url, json=data)
    res = response.json()
    if res['status'] is True:
        r_data = res['data']
        for item in r_data:
            print(item)
    else:
        print(res)


def find_from_dir(directory_name, questions_set):
    files = os.listdir(directory_name)
    for file_item in files:
        if file_item.startswith("~$"):
            continue
        file_path = os.path.join(directory_name, file_item).decode("gbk")
        items = os.path.split(file_path)

        if os.path.isfile(file_path) is False:
            continue
        elif file_path.endswith("答案.docx") is True:
            continue
        elif file_path.endswith(".doc") is True:
            if os.path.exists(file_path + "x"):
                continue
            continue
            # file_path = doc_to_docx(file_path)
        elif file_path.endswith(".docx") is False:
            print(u"跳过文件 %s" % file_path)
            continue
        if AnswerLocation.is_file(questions_set.answer_location):
            r, msg = handle_exam_with_answer(file_path, questions_set)
        else:
            r, msg = handle_exam_no_answer(file_path, questions_set)
        print(msg)
        questions_set.clear()


def download_questions(exam_no, select_mode):
    url = '%s/exam/questions/' % remote_host
    response = req.get(url, params={'exam_no': exam_no,
                                    'select_mode': select_mode,
                                    'start_no': 0,
                                    'no_rich': True})
    # print(response.text)
    resp = response.json()

    data = resp['data']
    no = 1
    with open("dq.txt", "w") as wd:
        for item in data:
            if item['select_mode'] != select_mode:
                continue
            wd.write('%s、' % no)
            wd.write(item['question_desc'])
            wd.write('\n')
            wd.write(item['answer'].strip())
            wd.write('\n\n')
            no += 1


def download_usage(exam_no, period_nos):
    t_nos = []
    with open('no.txt', 'r') as r:
        lines = r.read().split('\n')
        for line in lines:
            nums = re.findall('\d+', line)
            if len(nums) <= 0:
                continue
            if len(nums) > 1:
                raise RuntimeError(line)
            t_nos.append({'no': int(nums[0]), 'nums': []})
    for no in period_nos:
        url = '%s/exam/usage/state' % remote_host
        response = req.get(url, params={'exam_no': exam_no,
                                        'period_no': no})
        resp = response.json()
        data = resp['data']
        for t_item in t_nos:
            _num = 0
            for d_item in data:
                if d_item['user_no'] == t_item['no']:
                    _num = d_item['num']
                    break
            t_item['nums'].append(_num)
    with open('usage.xls', 'w') as wu:
        for t_item in t_nos:
            _lines = [t_item['no']]
            _lines.extend(t_item['nums'])
            r_lines = [str(i) for i in _lines]
            wu.write('\t'.join(r_lines))
            wu.write('\n')


if __name__ == "__main__":
    login(remote_host, "admin", "admin")
    # find_from_dir(r'D:\Project\word\app\upload')

    # exam_no = 1575333741 # 专升本经济学题库 试用版
    exam_no = 1585396371  # 本地 测试题库2
    exam_no = 1594597891  # 专升本经济学题库 搜题版

    # 538 + 319
    # 会员版 to 试用版
    # transfer_exam(1570447137, 4295, 4357, 1575333741)
    # 会员版 to 搜题版
    # transfer_exam(1570447137, 0, 20000, 1594597891, random=True)
    upload_dir = r'D:\Project\word\app\upload'
    items = os.listdir(upload_dir)
    d_path = os.path.join(upload_dir, items[0])
    # d_path = os.path.join(upload_dir, '2020年经济学真题.docx')
    keys = ['answer', 'question_desc']
    # keys.append(['options'])
    exam_name = items[0].rsplit(".", 1)[0]
    s_kwargs = dict(exam_no=exam_no, dry_run=True, set_mode=False,
                    file_path=d_path,
                    question_subject=0, # 0-微观经济学 1-宏观经济学 2-政治经济学
                    answer_location=AnswerLocation.file(), #  单独的答案文件
                    set_keys=keys)

    s_kwargs['set_source'] = True  # 设置题目来源 一般真题需要设置
    s_kwargs['exam_name'] = exam_name  # 设置题目来源 一般真题需要设置
    # s_kwargs['inside_mark_prefix'] = '2008年经济学真题多选判断'
    q_set = QuestionSet(**s_kwargs)
    # d = r'D:/Project/word/app/upload'
    # download_questions(1569283516, 2)
    handle_exam(d_path, q_set)

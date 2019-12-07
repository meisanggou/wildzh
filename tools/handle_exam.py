# !/usr/bin/env python
# coding: utf-8

import cv2
import json
import os
import re
import requests
import subprocess
import uuid


from read_xml import read_docx, read_answers_docx

__author__ = 'zhouhenglc'

req = requests.session()
headers = {"User-Agent": "jyrequests"}
req.headers = headers
remote_host = "https://meisanggou.vicp.net"
remote_host = "http://127.0.0.1:2400"
remote_host = "https://wild.gene.ac"

exec_file_dir, exec_file_name = os.path.split(os.path.abspath(__file__))
EXE_WMF_TO_PNG = os.path.join(exec_file_dir, "Wmf2Png.exe")

REAL_UPLOAD = False


def execute_cmd(cmd):
    sub_pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # sub_pro.wait()
    output = "\n".join(sub_pro.communicate())
    return sub_pro.returncode, output


def wmf_2_png(wmf_path, width, height, multiple=3):
    cmd = [EXE_WMF_TO_PNG, wmf_path, width, height, str(multiple)]
    code, output = execute_cmd(cmd)
    return output.strip()


def _clip_pic(pic_file, clip_data):
    file_values = pic_file.rsplit(".", 1)
    clip_pic_path = "".join(file_values[:-1])
    clip_pic_path += ".clip-%s.%s" % (uuid.uuid4().hex, file_values[-1])
    img = cv2.imread(pic_file)
    height = img.shape[0]
    width = img.shape[1]
    start_y = int(height * (clip_data[1] / 100.0))
    end_y = int(height - (height * (clip_data[3] / 100.0)))
    start_x = int(width * (clip_data[0] / 100.0))
    end_x = int(width - (width * (clip_data[2] / 100.0)))
    cropped = img[start_y:end_y, start_x:end_x]  # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imwrite(clip_pic_path, cropped)
    return clip_pic_path


def login(user_name, password):
    url = remote_host + "/user/login/password/"
    data = dict(user_name=user_name, password=password, next="/exam/")
    response = req.post(url, json=data)
    print(response.text)


def req_max_no(exam_no):
    url = remote_host + "/exam/questions/no/"
    response = req.get(url, params=dict(exam_no=exam_no))
    res = response.json()
    return res["data"]


def post_questions(question_set, dry_run=False, set_source=False):
    exam_no = question_set.exam_no
    no_info = req_max_no(exam_no)
    next_no = no_info["next_no"]
    url = remote_host + "/exam/questions/?exam_no=%s" % exam_no
    question_no = next_no
    for q_item in question_set:
        q_item_d = q_item.to_exam_dict()
        q_item_d["question_no"] = question_no
        if set_source:
            q_item_d["question_source"] = question_set.exam_name
        else:
            q_item_d["question_source"] = ""
        q_item_d["question_subject"] = 0
        if dry_run:
            print(json.dumps(q_item_d))
        if not dry_run:
            resp = req.post(url, json=q_item_d)
            print(resp.text)
        question_no += 1


def replace_media(text, q_rl, cache_rl, dry_run):
    media_comp = re.compile(r"(\[\[([a-z0-9]+?):([\d.]+?):([\d.]+?)(|:[\d\.\-|]+?)\]\])", re.I)
    found_rs = media_comp.findall(text)
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
        r_url = upload_media(m_id, q_rl, width, height, cache_rl, clip_data, dry_run)
        text = text.replace(r_t, "[[%s:%s:%s]]" % (r_url, width, height))
    return text


def upload_media(r_id, rl, width, height, cache_rl, clip_data=None, dry_run=False):
    if r_id in cache_rl:
        return cache_rl[r_id]

    o_pic = rl[r_id]
    o_pic_ext = o_pic.rsplit(".")[-1].lower()
    if o_pic_ext in ("jpeg", "png"):
        png_file = o_pic
    else:
        png_file = wmf_2_png(rl[r_id], width, height)
    if clip_data is not None:
        # 需要裁剪
        for i in range(4):
            if clip_data[i] == "":
                clip_data[i] = 0
            elif clip_data[i].startswith("-"):
                clip_data[i] = 0
            else:
                clip_data[i] = float(clip_data[i]) / 1000.0
        png_file = _clip_pic(png_file, clip_data)
    if dry_run:
        return "/dummy/%s" % r_id
    url = remote_host + "/exam/upload/"
    files = dict(pic=open(png_file, "rb"))
    resp = req.post(url, files=files)
    return resp.json()["data"]["pic"]


def handle_exam_no_answer(exam_no, file_path, select_mode=None):
    uploaded_q_rl = dict()
    exam_name = os.path.basename(file_path).rsplit(".", 1)[0]
    print("start handle %s" % exam_name)

    with read_docx(file_path, select_mode=select_mode) as rd:
        question_set, q_rl = rd
        question_set.exam_no = exam_no
        if question_set.length <= 0:
            raise RuntimeError("没发现题目")
        for q_item in question_set:
            q_no = q_item.no
            # 开始上传 题目
            # 获取题目描述中的图片
            q_item.desc = replace_media(q_item.desc, q_rl, uploaded_q_rl)

            # 获取选项中的图片
            for option in q_item.options:
                option.desc = replace_media(option.desc, q_rl, uploaded_q_rl)
            # 获取答案中的图片
            # q_item.answer = replace_media(q_item.answer, aw_rl, uploaded_aw_rl)
            q_item.inside_mark = "%s %s" % (exam_name, q_no)
        post_questions(question_set)
    return True, "success"


def handle_exam_with_answer(exam_no, file_path, select_mode=None,
                            dry_run=False, set_source=False):
    uploaded_aw_rl = dict()
    uploaded_q_rl = dict()
    exam_name = os.path.basename(file_path).rsplit(".", 1)[0]
    print(file_path)
    answer_file = file_path.replace(".docx", u"答案.docx")
    if os.path.exists(answer_file) is False:
        msg = ("Ignore %s, not Answer" % file_path)
        return False, msg
    print("start handle %s" % exam_name)

    with read_docx(file_path, select_mode) as rd, \
            read_answers_docx(answer_file, select_mode) as rad:
        question_set, q_rl = rd
        question_set.exam_no = exam_no
        answers_dict, aw_rl = rad
        if question_set.length <= 0:
            raise RuntimeError("没发现题目")
        for q_item in question_set:
            q_no = q_item.no
            # 判定是否包含答案

            if q_no not in answers_dict:
                print(exam_name)
                raise RuntimeError("lack answer %s" % q_item.no)
            q_item.set_answer(answers_dict[q_no])
            # 开始上传 题目
            # 获取题目描述中的图片
            q_item.desc = replace_media(q_item.desc, q_rl, uploaded_q_rl, dry_run)

            # 获取选项中的图片
            for option in q_item.options:
                option.desc = replace_media(option.desc, q_rl, uploaded_q_rl, dry_run)
            # 获取答案中的图片
            q_item.answer = replace_media(q_item.answer, aw_rl, uploaded_aw_rl, dry_run)
            q_item.inside_mark = "%s %s" % (exam_name, q_no)
        post_questions(question_set, dry_run, set_source)
    return True, "success"


def upload_js_with_answer(exam_no, file_path):
    login("admin", "admin")
    return handle_exam_with_answer(exam_no, file_path, 4)


def update_xz_no_answer(exam_no, file_path):
    login("admin", "admin")
    return handle_exam_no_answer(exam_no, file_path, 1)


def transfer_exam(s_exam, start_no, end_no, t_exam):
    url = remote_host + '/exam/transfer'
    data = {'source_exam_no': s_exam, 'start_no': start_no,
            'end_no': end_no, 'target_exam_no': t_exam}
    response = req.post(url, json=data)
    res = response.json()
    if res['status'] is True:
        r_data = res['data']
        for item in r_data:
            print(item)
    else:
        print(data)


def find_from_dir(exam_no, directory_name, dry_run, set_source):
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
        try:
            r, msg = handle_exam_with_answer(exam_no, file_path,
                                             dry_run=dry_run,
                                             set_source=set_source)
            print(msg)
        except Exception as e:
            print(e)


def download_questions(exam_no, select_mode):
    url = '%s/exam/questions/' % remote_host
    response = req.get(url, params={'exam_no': exam_no,
                                    'select_mode': select_mode})
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


if __name__ == "__main__":
    login("admin", "admin")
    # find_from_dir(r'D:\Project\word\app\upload')
    exam_no = 1567506833  # 测试包含图片
    exam_no = 1569283516  # 专升本经济学题库
    # exam_no = 1570447137  # 专升本经济学题库2
    # exam_no = 1573464937  # 英语托业
    # transfer_exam(exam_no, 74, 146, 1575333741)
    # update_xz_no_answer(exam_no, u'D:/Project/word/app/upload/英语.docx')
    # print(all_members)
    # d_path = ur'D:\Project\word\河南省专升本经济学测试题（二十）.docx'
    # read_docx(d_path)

    d = r'D:/Project/word/app/upload'
    # find_from_dir(exam_no, d, dry_run=True, set_source=False)
    # download_questions(1569283516, 2)

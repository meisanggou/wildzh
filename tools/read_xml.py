# !/usr/bin/env python
# coding: utf-8

from contextlib import contextmanager
import cv2
import json
import os
import pdb
import re
import requests
import shutil
import sys
import subprocess
import tempfile
import traceback
import uuid
from win32com import client as wc
import xml.dom.minidom as minidom
import zipfile

from parse_option import ParseOptions

reload(sys)
sys.setdefaultencoding('utf8')

exec_file_dir, exec_file_name = os.path.split(os.path.abspath(__file__))
EXE_WMF_TO_PNG = os.path.join(exec_file_dir, "Wmf2Png.exe")

req = requests.session()
headers = {"User-Agent": "jyrequests"}
req.headers = headers
remote_host = "https://meisanggou.vicp.net"
remote_host = "http://127.0.0.1:2400"
remote_host = "https://wild.gene.ac"


Q_TYPE_COMP = re.compile(u"((一|二|三|四|五)、|^)(单选|选择|名词解释|简答题|计算题|论述题)")
S_ANSWER_COMP = re.compile(r"(\d+)-(\d+)([a-d]+)", re.I)
G_SELECT_MODE = [u"无", u"选择", u"名词解释", u"简答题", u"计算题", u"论述题"]

REAL_UPLOAD = False


def get_select_mode(content):
    fr = Q_TYPE_COMP.findall(content)
    if len(fr) != 1:
        return -1
    s = fr[0][2]
    if s in G_SELECT_MODE:
        return G_SELECT_MODE.index(s)
    if s in (u"单选", u"单选题"):
        return 1
    raise RuntimeError("Bad select mode %s" % s)


def replace_special_space(s):
    for c in (u"\u3000", u"\xa0"):
        s = s.replace(c, " ")
    # for c in (u"\u6bb5", ):
    #     s = s.replace(c, "\n")
    return s


@contextmanager
def extract_docx(docx_path):
    temp_dir_name = "_wildzh_%s" % uuid.uuid4().hex
    temp_dir = os.path.join(tempfile.gettempdir(), temp_dir_name)
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    zf = zipfile.ZipFile(docx_path)
    zf.extractall(path=temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


def doc_to_docx(doc_path):
    word = wc.Dispatch("Word.Application")
    doc = word.Documents.Open(doc_path)
    docx_path = doc_path + "x"
    doc.SaveAs(docx_path, 12)  # 12为docx
    doc.Close()
    word.Quit()
    return docx_path


def _get_node(p_node, node_name):
    return filter(lambda x: x.nodeName == node_name, p_node.childNodes)


def _get_one_node(p_node, node_name):
    children = _get_node(p_node, node_name)
    if len(children) != 1:
        raise RuntimeError("Fond not 1(is %s) %s" % (len(children), node_name))
    return children[0]


def get_deep_node(p_node, node_name):
    _names = node_name.split(".")
    p_nodes = [p_node]
    for name in _names:
        p_nodes = _get_node(p_nodes[0], name)
        if len(p_nodes) <= 0:
            return []
    return p_nodes


def get_deep_one_node(p_node, node_name):
    nodes = get_deep_node(p_node, node_name)
    return nodes[0]


def analysis_style(style):
    h_comp = re.compile(r"height:([\d.]+?)pt")
    w_comp = re.compile(r"width:([\d.]+?)(pt|in)")
    try:
        height = h_comp.findall(style)[0]
        width, unit = w_comp.findall(style)[0]
        if unit == "in":
            width = float(width) * 71.6
    except IndexError as e:
        print(style)
        pdb.set_trace()
        return 0, 0
    return width, height


def _handle_drawing(drawing_node):
    # 根据图片嵌入方式不同
    # 嵌入式 <w:drawing>直接是<wp:inline
    # 浮于文字上方 <w:drawing>直接是wp:anchor
    # 可能是文本框
    blip_fills = drawing_node.getElementsByTagName("pic:blipFill")
    if len(blip_fills) <= 0:
        return None
    blip_fill = blip_fills[0]
    pic_el = blip_fill.parentNode
    pic_extent_el = drawing_node.getElementsByTagName("wp:extent")[0]
    cx = int(pic_extent_el.getAttribute("cx"))
    cy = int(pic_extent_el.getAttribute("cy"))
    lip = _get_one_node(blip_fill, "a:blip")
    r_id = lip.getAttribute("r:embed")
    values = "%s:%s:%s" % (r_id, cx / 10000, cy / 10000)
    src_rects = _get_node(blip_fill, "a:srcRect")  # 可能不存在裁剪
    if len(src_rects) == 1:
        src_rect = src_rects[0]
        left = src_rect.getAttribute("l")
        top = src_rect.getAttribute("t")
        right = src_rect.getAttribute("r")
        bottom = src_rect.getAttribute("b")
        values += ":%s|%s|%s|%s" % (left, top, right, bottom)
    print(values)
    return "[[%s]]" % values


def handle_paragraph(p_node):
    run_children = _get_node(p_node, "w:r")
    p_contents = []
    is_bold = True
    for child in run_children:
        text_children = _get_node(child, "w:t")
        for c in text_children:
            p_contents.append(c.firstChild.nodeValue)

        # 获得
        object_children = _get_node(child, "w:object")
        for oc in object_children:
            v_shape = _get_node(oc, "v:shape")[0]
            v_shape_style = v_shape.getAttribute("style")
            width, height = analysis_style(v_shape_style)
            r_id = _get_node(v_shape, "v:imagedata")[0].getAttribute("r:id")
            p_contents.append("[[%s:%s:%s]]" % (r_id, width, height))
        # 获得段内换行
        br_children = _get_node(child, "w:br")
        if len(br_children) == 1:
            p_contents.append("\n")
        # 获得直接嵌入的图片
        drawing_nodes = _get_node(child, "w:drawing")
        # 获得兼容显示的图片  可能是文本框
        # mc:AlternateContent
        mc_drawings = get_deep_node(child, "mc:AlternateContent.mc:Choice.w:drawing")
        drawing_nodes.extend(mc_drawings)
        if len(drawing_nodes) > 0:
            drawing_data = _handle_drawing(drawing_nodes[0])
            if drawing_data is not None:
                p_contents.append(drawing_data)

    if len(p_contents) <= 0:
        is_bold = False
    # TODO 返回字符串是否加粗

    return "".join(p_contents)


def handle_rels(rels_path):
    rels_dom = minidom.parse(rels_path)
    relationships_node = rels_dom.firstChild
    relationships = dict()
    for rs in _get_node(relationships_node, "Relationship"):
        r_id = rs.getAttribute("Id")
        target = rs.getAttribute("Target")
        relationships[r_id] = target
    return relationships


def get_question(question_items):
    if len(question_items) == 0:
        return None
    desc = ""
    q_no = question_items[0]
    i = 1
    while i < len(question_items):
        qs_item = question_items[i]
        if re.match("A|B|C|D", qs_item, re.I) is not None:
            break
        desc += qs_item
        i += 1
    parse_o = ParseOptions()
    parse_o.parse(question_items[i:])
    real_options = parse_o.to_list()
    r_options = map(lambda x: dict(desc=x, score=0), real_options)
    return dict(no=q_no, desc=desc, options=r_options)


def get_qa_question(question_items):
    if len(question_items) == 0:
        return None
    q_no = question_items[0]
    desc = "\n".join(question_items[1:])
    options = [dict(desc=u"会", score=1),
               dict(desc=u"不会", score=0)]
    return dict(no=q_no, desc=desc, options=options)


def handle_docx_main_xml(xml_path, *args):
    dom = minidom.parse(xml_path)
    root = dom.documentElement
    body = _get_one_node(root, "w:body")
    questions_s = []
    current_q_type = None
    current_question = []
    current_question_no = 0
    s_c = args
    m_compile = re.compile(ur"(\d+)(%s)" % "|".join(map(lambda x: re.escape(x), s_c)))

    def _get_question():
        if not current_question:
            return
        if current_question[0] == 1:
            q_item = get_question(current_question[1:])
        else:
            q_item = get_qa_question(current_question[1:])
        if q_item is not None:
            q_item["select_mode"] = current_question[0]
            questions_s.append(q_item)

    for node in body.childNodes:
        if node.nodeName != "w:p":
            continue
        p_content = handle_paragraph(node).strip()
        if len(p_content) <= 0:
            continue
        # 判断是否是题目类型
        _q_tpe = get_select_mode(p_content)
        if _q_tpe > 0:
            current_q_type = _q_tpe
            continue
        # 判断是否是题目
        is_question_item = False
        m_no = m_compile.match(p_content)
        if m_no is None:
            if current_question:
                # 有可能有些题目，题号后面没有逗号顿号, 我们以当前题号+1 尝试判定
                if p_content.startswith("%s" % (current_question_no + 1)):
                    is_question_item = True
                    q_no = current_question_no + 1
                    s_q_no = str(q_no)
                    p_content = p_content[len(s_q_no):]
        else:
            is_question_item = True
            q_no = int(m_no.groups()[0])
            p_content = p_content[len("".join(m_no.groups())):]
        if is_question_item:
            _get_question()
            current_question = [current_q_type, q_no]
            current_question_no = q_no
            current_question.append(p_content)
        else:
            if current_question:
                current_question.append(p_content)
    if len(current_question) > 0:
        _get_question()
    return questions_s


def read_docx_xml(root_dir):
    xml_path = os.path.join(root_dir, 'word', 'document.xml')
    questions_s = handle_docx_main_xml(xml_path, ".", u"、", u"．")
    style_path = os.path.join(root_dir, 'word', '_rels', "document.xml.rels")
    relationships = handle_rels(style_path)
    for key in relationships.keys():
        relationships[key] = os.path.join(root_dir, "word", relationships[key])
    return questions_s, relationships


@contextmanager
def read_docx(docx_path):
    with extract_docx(docx_path) as temp_dir:
        questions_s, relationships = read_docx_xml(temp_dir)
        yield [questions_s, relationships]
        pass


def get_answers(answer_items):
    aw_dict = dict()
    s_ac = ["A", "B", "C", "D"]
    for a_item in answer_items:
        sp_items = S_ANSWER_COMP.findall(a_item)
        for start, end, answers in sp_items:
            i_start, i_end = int(start), int(end)
            if len(answers) != i_end - i_start + 1:
                raise RuntimeError("not right format: %s-%s%s" % (start, end, answers))
            for i in range(i_start, i_end + 1):
                if i in aw_dict:
                    raise RuntimeError("repeated answers %s" % i)
                aw_dict[i] = s_ac.index(answers[i - i_start].upper())
    return aw_dict


def get_qa_answers(answer_items):
    aw_dict = dict()
    qa_aw_comp = re.compile(ur"^(\d+)(.|、|．)([\s\S]*)")
    current_no = -1
    current_answer = ""
    answer_items = map(lambda x: x.strip(), answer_items)
    for item in answer_items:
        # 判断是否是答案开始
        found_items = qa_aw_comp.findall(item)
        if found_items:
            found_item = found_items[0]
            next_no = int(found_item[0])
            if next_no < current_no:
                # 不允许出现同一个答案区域，出现题号下降。防止答案里出现小题题号，出现误判
                current_answer += "\n" + item
                continue
            if current_no != -1:
                if current_no in aw_dict:
                    raise RuntimeError("repeated answers %s" % current_no)
                aw_dict[current_no] = current_answer
            current_no = next_no
            current_answer = found_item[2]
        else:
            current_answer += "\n" + item
    if current_no != -1:
        if current_no in aw_dict:
            raise RuntimeError("repeated answers %s" % current_no)
        aw_dict[current_no] = current_answer
    return aw_dict


def handle_answers_docx_main_xml(xml_path):
    dom = minidom.parse(xml_path)
    root = dom.documentElement
    body = root.firstChild
    current_q_type = -1
    current_answers_area = []
    answers_dict = dict()

    def _get_answers():
        if current_q_type < 0:
            return
        if current_q_type == 1:
            # 获取选择题答案
            sub_aw = get_answers(current_answers_area)
        else:
            sub_aw = get_qa_answers(current_answers_area)
        for i in sub_aw.keys():
            if i in answers_dict:
                raise RuntimeError("repeated answers %s" % i)
        answers_dict.update(sub_aw)

    for node in body.childNodes:
        if node.nodeName != "w:p":
            continue
        p_content = handle_paragraph(node).strip()

        if len(p_content) <= 0:
            continue
        _q_type = get_select_mode(p_content)
        if _q_type >= 0:
            # match到关键字 且字符串长度不能
            _get_answers()
            current_q_type = _q_type
            current_answers_area = []
            continue
        current_answers_area.append(p_content)
    if len(current_answers_area) > 0:
        _get_answers()
    return answers_dict


def read_answers_docx_xml(root_dir):
    xml_path = os.path.join(root_dir, 'word', 'document.xml')
    answers = handle_answers_docx_main_xml(xml_path)
    style_path = os.path.join(root_dir, 'word', '_rels', "document.xml.rels")
    relationships = handle_rels(style_path)
    for key in relationships.keys():
        relationships[key] = os.path.join(root_dir, "word", relationships[key])
    return answers, relationships


@contextmanager
def read_answers_docx(docx_path):
    with extract_docx(docx_path) as temp_dir:
        print(temp_dir)
        answers, relationships = read_answers_docx_xml(temp_dir)
        yield [answers, relationships]
        pass


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


def upload_media(r_id, rl, width, height, cache_rl, clip_data=None):
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
    if REAL_UPLOAD is False:
        return "/dummy/%s" % r_id
    url = remote_host + "/exam/upload/"
    files = dict(pic=open(png_file, "rb"))
    resp = req.post(url, files=files)
    return resp.json()["data"]["pic"]


def replace_media(text, q_rl, cache_rl):
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
        r_url = upload_media(m_id, q_rl, width, height, cache_rl, clip_data)
        text = text.replace(r_t, "[[%s:%s:%s]]" % (r_url, width, height))
    return text


def handle_exam(file_path):
    exam_no = 1567506833  # 测试包含图片
    exam_no = 1570447137  # 专升本经济学题库2
    no_info = req_max_no(exam_no)
    next_no = no_info["next_no"]

    uploaded_aw_rl = dict()
    uploaded_q_rl = dict()
    exam_name = os.path.basename(file_path).rsplit(".", 1)[0]
    answer_file = file_path.replace(".docx", u"答案.docx")
    if os.path.exists(answer_file) is False:
        msg = ("Ignore %s, not Answer" % file_path)
        return False, msg
    print("start handle %s" % exam_name)

    with read_docx(file_path) as rd, read_answers_docx(answer_file) as rad:
        question_list, q_rl = rd
        answers_dict, aw_rl = rad
        if len(question_list) <= 0:
            raise RuntimeError("没发现题目")
        for q_item in question_list:
            q_no = q_item["no"]
            # 判定是否包含答案
            if q_no not in answers_dict:

                print(exam_name)
                raise RuntimeError("lack answer %s" % q_item["no"])
            if q_item["select_mode"] == 1:  # 选择题
                q_item["options"][answers_dict[q_no]]["score"] = 1
                q_item["answer"] = ""
            else:
                q_item["answer"] = answers_dict[q_no]
            # 开始上传 题目
            # 获取题目描述中的图片
            q_item["desc"] = replace_media(q_item["desc"], q_rl, uploaded_q_rl)

            # 获取选项中的图片
            for option in q_item["options"]:
                option["desc"] = replace_media(option["desc"], q_rl, uploaded_q_rl)
            # 获取答案中的图片
            q_item["answer"] = replace_media(q_item["answer"], aw_rl, uploaded_aw_rl)
            q_item["inside_mark"] = "%s %s" % (exam_name, q_no)
        post_questions(exam_name, exam_no, next_no, question_list)
    return True, "success"


def find_from_dir(directory_name):
    files = os.listdir(directory_name)
    for file_item in files:
        if file_item.startswith("~$"):
            continue
        file_path = os.path.join(directory_name, file_item).decode("gbk")
        items = os.path.split(file_path)

        if os.path.isfile(file_path) is False:
            continue
        elif file_path.endswith(u"答案.docx") is True:
            continue
        elif file_path.endswith(".doc") is True:
            if os.path.exists(file_path + "x"):
                continue
            file_path = doc_to_docx(file_path)
        elif file_path.endswith(".docx") is False:
            print(u"跳过文件 %s" % file_path)
            continue
        h_r, msg = handle_exam(file_path)
        if h_r is False:
            with open("error.text", "w") as we:
                we.write(file_path)
                we.write(msg)
            print(msg)
        # if len(members) <= 0:
        #     print(u"请检查文件%s" % file_path)
        # all_member.extend(members)


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


def post_questions(exam_name, exam_no, start_no, questions_obj):
    url = remote_host + "/exam/questions/?exam_no=%s" % exam_no
    question_no = start_no
    for q_item in questions_obj:
        q_item["question_no"] = question_no
        q_item["question_source"] = exam_name
        q_item["question_subject"] = 0
        q_item["question_desc"] = q_item.pop("desc").strip()
        print(json.dumps(q_item))
        # if REAL_UPLOAD is True:
        #     resp = req.post(url, json=q_item)
        #     print(resp.text)
        question_no += 1


if __name__ == "__main__":
    login("admin", "admin")
    find_from_dir(r'D:\Project\word\app\upload')
    # print(all_members)
    # d_path = ur'D:\Project\word\河南省专升本经济学测试题（二十）.docx'
    # read_docx(d_path)

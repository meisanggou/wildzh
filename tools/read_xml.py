# !/usr/bin/env python
# coding: utf-8

from contextlib import contextmanager
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
    return p_nodes


def analysis_style(style):
    h_comp = re.compile(r"height:([\d.]+?)pt")
    w_comp = re.compile(r"width:([\d.]+?)pt")
    height = h_comp.findall(style)[0]
    width = w_comp.findall(style)[0]
    return width, height


def handle_paragraph(p_node):
    run_children = _get_node(p_node, "w:r")
    p_contents = []
    is_bold = True
    for child in run_children:
        text_children = _get_node(child, "w:t")
        for c in text_children:
            p_contents.append(c.firstChild.nodeValue)
        # if len(text_children) > 0 and is_bold:
        #     bold_children = get_deep_node(child, "w:rPr.w:bCs")
        #     if len(bold_children) <= 0:
        #         is_bold = False
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
    if len(p_contents) <= 0:
        is_bold = False
    # TODO 返回字符串是否加粗
    # if is_bold is True and len(p_contents) > 0:
    #     print("---------------------rpr")
    #     print("".join(p_contents))
    # p_bold_children = get_deep_node(p_node, "w:pPr.w:rPr.w:bCs")
    # if len(p_bold_children) > 0:
    #     if p_bold_children[0].getAttribute("w:val") != "0":
    #         print("---------------------ppr")
    #         print("".join(p_contents))
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


def get_question(question_items, *args):
    if len(question_items) == 0:
        return None
    s_c = args
    desc = ""
    q_no = question_items[0]
    i = 1
    while i < len(question_items):
        qs_item = question_items[i]
        if re.match("A|B|C|D", qs_item, re.I) is not None:
            break
        desc += qs_item
        i += 1
    options = []

    def replace(match_r):
        mgs = match_r.groups()
        return "\n"
    # print(u"(A|B|C|D)(%s)" % "|".join(map(lambda x: re.escape(x), s_c)))
    r_compile = re.compile(u"(^|\s)(A|B|C|D)(%s)" % "|".join(map(lambda x: re.escape(x), s_c)))
    #  有些选项 A B C D后面没有点
    rb_compile = re.compile(u"(^|\s)(A|B|C|D)(%s|)" % "|".join(map(lambda x: re.escape(x), s_c)))

    for item in question_items[i:]:
        item = replace_special_space(item)
        r_item = r_compile.sub(replace, item)
        options.extend(r_item.split("\n"))
    real_options = map(lambda x: x.strip(), options)
    real_options = filter(lambda x: len(x) > 0, real_options)
    if len(real_options) < 4:
        #  有些选项 A B C D后面没有点
        options_s = "\n".join(question_items[i:])
        r_options_s = rb_compile.sub(replace, options_s)
        real_options = r_options_s.split("\n")
        real_options = map(lambda x: x.strip(), real_options)
        real_options = filter(lambda x: len(x) > 0, real_options)
    if len(real_options) != 4:
        for r_o in real_options:
            print(r_o)
        print(q_no)
        for item in question_items:
            print(item)
        raise RuntimeError("")
        return None
    # for r_o in real_options:
    #     print(r_o)
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
    body = root.firstChild
    questions_s = []
    current_q_type = None
    current_question = []
    s_c = args
    m_compile = re.compile(ur"(\d+)(%s)" % "|".join(map(lambda x: re.escape(x), s_c)))

    def _get_question():
        if current_question[0] == 1:
            q_item = get_question(current_question[1:], ".", u"、", u"．")
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
        m_no = m_compile.match(p_content)
        if m_no is not None:
            _get_question()
            q_no = int(m_no.groups()[0])
            current_question = [current_q_type, q_no]
            current_question.append(p_content[len("".join(m_no.groups())):])
        else:
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


def upload_media(r_id, rl, width, height, cache_rl):
    if r_id in cache_rl:
        return cache_rl[r_id]

    png_file = wmf_2_png(rl[r_id], width, height)
    url = remote_host + "/exam/upload/"
    files = dict(pic=open(png_file, "rb"))
    resp = req.post(url, files=files)
    return resp.json()["data"]["pic"]


def replace_media(text, q_rl, cache_rl):
    media_comp = re.compile(r"(\[\[([a-z0-9]+?):([\d.]+?):([\d.]+?)\]\])", re.I)
    found_rs = media_comp.findall(text)
    for r_item in found_rs:
        r_t = r_item[0]
        m_id = r_item[1]
        width = r_item[2]
        height = r_item[3]
        r_url = upload_media(m_id, q_rl, width, height, cache_rl)
        text = text.replace(r_t, "[[%s:%s:%s]]" % (r_url, width, height))
    return text


def handle_exam(file_path):
    exam_no = 1567506833
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
        for q_item in question_list:
            q_no = q_item["no"]
            # 判定是否包含答案
            if q_no not in answers_dict:
                pdb.set_trace()
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
    all_member = []
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
    # for mem in all_member:
    #     print("\t".join(mem))
    all_member.sort(key=lambda x: x[3])
    return all_member


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
        resp = req.post(url, json=q_item)
        print(resp.text)
        question_no += 1


login("admin", "admin")
find_from_dir(r'D:\Project\word\app\upload')
# print(all_members)
# d_path = ur'D:\Project\word\河南省专升本经济学测试题（二十）.docx'
# read_docx(d_path)

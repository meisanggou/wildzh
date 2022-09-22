# !/usr/bin/env python
# coding: utf-8

import os
import pdb
import re
# from win32com import client as wc
import xml.dom.minidom as minidom
from wildzh.tools import constants
from wildzh.tools.parse.answer import Answer
from wildzh.tools.parse.exception import QuestionTypeNotMatch
from wildzh.tools.parse.option_type import OptionType
from wildzh.tools.parse_question import ParseQuestion, QuestionType
from wildzh.tools.parse_question import AnswerSet, AnswerLocation




def replace_special_space(s):
    for c in (u"\u3000", u"\xa0"):
        s = s.replace(c, " ")
    # for c in (u"\u6bb5", ):
    #     s = s.replace(c, "\n")
    return s


def _get_node(p_node, node_name):
    f =  filter(lambda x: x.nodeName == node_name, p_node.childNodes)
    return list(f)

def _get_nodes(p_node, node_names):
    f =  filter(lambda x: x.nodeName in node_names, p_node.childNodes)
    return list(f)


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
    values = "%s$%s$%s" % (r_id, cx / 10000, cy / 10000)
    src_rects = _get_node(blip_fill, "a:srcRect")  # 可能不存在裁剪
    if len(src_rects) == 1:
        src_rect = src_rects[0]
        left = src_rect.getAttribute("l")
        top = src_rect.getAttribute("t")
        right = src_rect.getAttribute("r")
        bottom = src_rect.getAttribute("b")
        values += "$%s|%s|%s|%s" % (left, top, right, bottom)

    return "[[%s]]" % values


def handle_paragraph(p_node):
    run_children = _get_nodes(p_node, ["w:r", "m:oMath"])
    p_contents = []
    is_bold = True
    for child in run_children:
        if child.nodeName == 'm:oMath':
            p_contents.append(constants.MATH_FILL)
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
            p_contents.append("[[%s$%s$%s]]" % (r_id, width, height))
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


def handle_docx_main_xml(docx_obj, *args, **kwargs):
    questions_set = kwargs.pop('questions_set')
    select_mode = questions_set.default_select_mode
    embedded_answer = AnswerLocation.is_embedded(questions_set.answer_location)
    current_q_type = questions_set.default_select_mode
    current_question = []
    current_question_no = 0
    s_c = args
    m_compile = re.compile(r"(\d+)(%s)" % "|".join(map(lambda x: re.escape(x), s_c)))

    def _get_question():
        if not current_question:
            return
        q_item = ParseQuestion.parse(current_question[1:],
                                     select_mode=current_question[0],
                                     embedded_answer=embedded_answer)

        if current_question[0] in (1, 6):
            if q_item.q_type != QuestionType.Choice:
                raise QuestionTypeNotMatch(current_question[1:],
                                           '题型应该是选择题，未在题目中发现选择题')
        elif current_question[0] in (7, ):
            if q_item.q_type != QuestionType.Judge:
                raise RuntimeError(u"问题类型解析错误 %s" % q_item.q_type)
        else:
            if q_item.q_type != QuestionType.QA:
                raise RuntimeError(u"问题类型解析错误 %s" % q_item.q_type)
        q_item.select_mode = current_question[0]
        questions_set.append(q_item)

    for p_content in docx_obj.read_paragraphs(handle_paragraph=handle_paragraph):
        # 判断是否是题目类型
        if not select_mode:
            _q_tpe = OptionType.detection_type(p_content)
            if _q_tpe > 0:
                current_q_type = _q_tpe
                continue
        # 判断是否是题目
        is_question_item = False
        m_no = m_compile.match(p_content)
        if m_no is None:
            # 有可能有些题目，题号后面没有逗号顿号, 我们以当前题号+1 尝试判定
            _com = re.compile('^%s[^\d]' % (current_question_no + 1))
            if _com.match(p_content):
                is_question_item = True
                s_q_no = '%s' % (current_question_no + 1)
                q_no = '%s?' % s_q_no
                p_content = p_content[len(s_q_no):]
        else:
            q_no = int(m_no.groups()[0])
            # 可能匹配到 小数点数字
            if m_no.groups()[1] == '.'and q_no == 0:
                pass
            else:
                is_question_item = True
                p_content = p_content[len("".join(m_no.groups())):]
        if is_question_item:
            _get_question()
            current_question = [current_q_type, q_no]
            if isinstance(q_no, int):
                current_question_no = q_no
            else:
                current_question_no = int(q_no[:-1])
            current_question.append(p_content)
        else:
            if current_question:
                current_question.append(p_content)
    if len(current_question) > 0:
        _get_question()
    return questions_set


def handle_answers_docx_main_xml(docx_obj, questions_set):
    select_mode = questions_set.default_select_mode
    current_q_type = select_mode
    current_answers_area = []
    answers_dict = AnswerSet()

    def _get_answers():
        if current_q_type is None:
            return
        if current_q_type < 0:
            return
        sub_aw = Answer.get_parser(current_q_type).parse_answers(
            current_answers_area)
        for item in sub_aw:
            answers_dict.add(item)

    for p_content in docx_obj.read_paragraphs(handle_paragraph=handle_paragraph):
        _q_type = OptionType.detection_type(p_content)
        if not select_mode:
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
        # elif file_path.endswith(".doc") is True:
        #     if os.path.exists(file_path + "x"):
        #         continue
        #     file_path = doc_to_docx(file_path)
        elif file_path.endswith(".docx") is False:
            print(u"跳过文件 %s" % file_path)
            continue
        # h_r, msg = handle_exam(file_path)
        # if h_r is False:
        #     with open("error.text", "w") as we:
        #         we.write(file_path)
        #         we.write(msg)
        #     print(msg)
        # if len(members) <= 0:
        #     print(u"请检查文件%s" % file_path)
        # all_member.extend(members)

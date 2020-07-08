# !/usr/bin/env python
# coding: utf-8

from contextlib import contextmanager
import os
import pdb
import re
# from win32com import client as wc
import xml.dom.minidom as minidom
from wildzh.tools.docx.object import DocxObject
from wildzh.tools.parse_question import ParseQuestion, QuestionType
from wildzh.tools.parse_question import Answer, AnswerSet, ParseAnswer, AnswerLocation

# reload(sys)
# sys.setdefaultencoding('utf8')


Q_TYPE_COMP = re.compile(u"((一|二|三|四|五|六)[、.]|^)(单选|单项|选择|名词解释|简答|简答题|计算|计算题|论述|论述题)")
S_ANSWER_COMP = re.compile(r"(\d+)(?:-|—)(\d+)([a-d]+)", re.I)
S_ANSWER_COMP2 = re.compile(r"(?:\s|^)(\d+)([a-d](?:\s|$))", re.I)
G_SELECT_MODE = [u"无", u"选择", u"名词解释", u"简答题", u"计算题", u"论述题"]


def get_select_mode(content):
    fr = Q_TYPE_COMP.findall(content)
    if len(fr) != 1:
        return -1
    s = fr[0][2]
    if s in G_SELECT_MODE:
        return G_SELECT_MODE.index(s)
    if s in (u"单选", u"单选题", u"单项"):
        return 1
    if s in (u"名词解释", u"名词"):
        return 2
    if s in (u"简答", u"简答题"):
        return 3
    if s in (u"计算", u"计算题"):
        return 4
    if s in (u"论述", u"论述题"):
        return 5
    raise RuntimeError("Bad select mode %s" % s)


def replace_special_space(s):
    for c in (u"\u3000", u"\xa0"):
        s = s.replace(c, " ")
    # for c in (u"\u6bb5", ):
    #     s = s.replace(c, "\n")
    return s


# def doc_to_docx(doc_path):
#     word = wc.Dispatch("Word.Application")
#     doc = word.Documents.Open(doc_path)
#     docx_path = doc_path + "x"
#     doc.SaveAs(docx_path, 12)  # 12为docx
#     doc.Close()
#     word.Quit()
#     return docx_path


def _get_node(p_node, node_name):
    f =  filter(lambda x: x.nodeName == node_name, p_node.childNodes)
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

        if current_question[0] == 1:
            if q_item.q_type != QuestionType.Choice:
                pdb.set_trace()
                raise RuntimeError(u"问题类型解析错误 %s".encode("gbk") % q_item.no)
        else:
            if q_item.q_type != QuestionType.QA:
                raise RuntimeError(u"问题类型解析错误")
        q_item.select_mode = current_question[0]
        questions_set.append(q_item)

    for p_content in docx_obj.read_paragraphs(handle_paragraph=handle_paragraph):
        # 判断是否是题目类型
        if not select_mode:
            _q_tpe = get_select_mode(p_content)
            if _q_tpe > 0:
                current_q_type = _q_tpe
                continue
        # 判断是否是题目
        is_question_item = False
        m_no = m_compile.match(p_content)
        if m_no is None:
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
    return questions_set


@contextmanager
def read_docx(docx_path, questions_set):
    with DocxObject(docx_path) as do:
        questions_s = handle_docx_main_xml(do, ".", u"、", u"．", ':',
                                       questions_set=questions_set)
        yield [questions_s, do.relationships]
        pass


def get_answers(answer_items, parse_answer):
    aw_dict = []
    for a_item in answer_items:
        sp_items = S_ANSWER_COMP.findall(a_item)
        for start, end, answers in sp_items:
            i_start, i_end = int(start), int(end)
            if len(answers) != i_end - i_start + 1:
                raise RuntimeError("not right format: %s-%s%s" % (start, end, answers))
            for i in range(i_start, i_end + 1):
                if i in aw_dict:
                    raise RuntimeError("repeated answers %s" % i)
                a = parse_answer.parse(answers[i - i_start])
                a.no = i
                aw_dict.append(a)
        sp_items2 = S_ANSWER_COMP2.findall(a_item)
        for no, answer in sp_items2:
            a = parse_answer.parse(answer)
            a.no = int(no)
            aw_dict.append(a)
    return aw_dict


def get_qa_answers(answer_items, parse_answer):
    aw_dict = []
    qa_aw_comp = re.compile(r"^(\d+)(.|、|．)([\s\S]*)")
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
            if next_no >= current_no + 10 and current_no > 0:
                # 不允许出现同一个答案区域，出现题号上升过快
                current_answer += "\n" + item
                continue
            if current_no != -1:
                if current_no in aw_dict:
                    raise RuntimeError("repeated answers %s" % current_no)
                a = parse_answer.parse(current_answer)
                a.no = current_no
                aw_dict.append(a)
            current_no = next_no
            current_answer = found_item[2]
        else:
            current_answer += "\n" + item
    if current_no != -1:
        a = parse_answer.parse(current_answer)
        a.no = current_no
        aw_dict.append(a)
    return aw_dict


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
        # if current_q_type == 5:
        #     pdb.set_trace()
        p_answer = ParseAnswer(current_q_type)
        if current_q_type == 1:
            # 获取选择题答案
            sub_aw = get_answers(current_answers_area, p_answer)

        else:
            sub_aw = get_qa_answers(current_answers_area, p_answer)
        for item in sub_aw:
            answers_dict.add(item)

    for p_content in docx_obj.read_paragraphs(handle_paragraph=handle_paragraph):
        _q_type = get_select_mode(p_content)
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


@contextmanager
def read_answers_docx(docx_path, questions_set):
    with DocxObject(docx_path) as do:
        answers = handle_answers_docx_main_xml(do, questions_set)
        yield [answers, do.relationships]
        pass


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


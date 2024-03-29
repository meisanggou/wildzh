# !/usr/bin/env python
# coding: utf-8

from functools import cmp_to_key
import re
import os
import shutil
import tempfile
import uuid
import zipfile
from wildzh.export import docx_obj
from wildzh.export.render_xml import write_xml


__author__ = 'meisa'

abs_dir = os.path.abspath(os.path.dirname(__file__))


OPTION_MAPPING = ["A", "B", "C", "D"]
cn_num = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一",
          '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']


class Counter(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        name = None
        if 'name' in kwargs:
            name = kwargs['name']
        elif len(args) > 1:
            name = args[0]
        if name in cls._instances:
            return cls._instances[name]
        o = object.__new__(cls)
        cls._instances[name] = o
        return o

    def __init__(self, name, index=10):
        self.name = name
        self._index = index

    @property
    def value(self):
        return self._index

    def plus(self):
        self._index += 1


def string_length(s):
    # if isinstance(s, str):
    #     s = s.decode("utf-8")
    all_ch = re.findall(u"[\u4E00-\u9FA5]+", s)
    plus_len = 0
    for item in all_ch:
        plus_len += len(item)
    return len(s) + plus_len


def download_file(path, upload_folder, save_dir, name):
    src = path.replace('/file', upload_folder)
    save_path = os.path.join(save_dir, name)
    shutil.copy(src, save_path)
    return save_path


def get_alone_answers(choice_blocks, answer_blocks, answer_mode='alone'):
    alone_answers = [docx_obj.ParagraphPageXmlObj().to_xml()]

    title_p = docx_obj.ParagraphXmlObj('答案', outline_level=1)
    alone_answers.append(title_p.to_xml())
    for c_block in choice_blocks:
        alone_answers.extend(
            docx_obj.BlockParent(
                c_block['mode'],
                c_block['questions'],
                answer_mode).get_answers())
    for ab in answer_blocks:
        alone_answers.extend(
            docx_obj.BlockParent(
                ab['mode'],
                ab['questions'],
                answer_mode).get_answers())
    return alone_answers


def _handle_rich_desc(rd_item, rid_c, rid_p):
    if isinstance(rd_item, dict):
        rid = "%s%s" % (rid_p, rid_c.value)
        rd_item['rid'] = rid
        rd_item['width'] = int(rd_item['width'] * 10000)
        rd_item['height'] = int(rd_item['height'] * 10000)
        rd_item['r_index'] = rid_c.value
        r_name = '%s.%s' % (rid, rd_item['url'].rsplit('.', 1)[-1])
        rd_item['name'] = r_name
        rid_c.plus()
        m_item = {'rid': rid, 'name': r_name, 'url': rd_item['url']}
        return m_item


def handle_choice_question(question, question_no, rid_c, rid_p):
    medias = []
    s_item = question
    for _r_item in s_item['question_desc_rich']:
        m_item = _handle_rich_desc(_r_item, rid_c, rid_p)
        medias.append(m_item)
    s_item['question_desc_rich'].insert(0, '%s.' % question_no)
    s_item["this_question_no"] = question_no

    max_score = -100
    right_index = -1
    right_option = ""
    max_option_len = 0
    for index in range(len(s_item["options"])):
        item = s_item["options"][index]
        o_len = 0
        _ll = []
        for dr_item in item['desc_rich']:
            if isinstance(dr_item, dict):
                o_len += dr_item['width'] / 10
                m_item = _handle_rich_desc(dr_item, rid_c, rid_p)
                medias.append(m_item)
            else:
                o_len += string_length(dr_item)
        item['desc_rich'].insert(0, '%s.' % OPTION_MAPPING[index])
        item['desc_rich'].extend(_ll)
        if o_len > max_option_len:
            max_option_len = o_len
        if "score" not in item:
            item["score"] = 0
        if item['score'] >= 1:
            right_option += OPTION_MAPPING[index]
        if item["score"] > max_score:
            max_score = item["score"]
            right_index = index
    if max_option_len <= 12:
        s_item["option_style"] = "t_four"
    elif max_option_len <= 28:
        s_item["option_style"] = "t_two"
    else:
        s_item["option_style"] = "one"
    s_item["right_option"] = right_option  # OPTION_MAPPING[right_index]
    return s_item, medias


def receive_data(question_items, select_modes, answer_mode):
    def _question_sort(a, b):
        # 按照政治经济学，微观经济学，宏观经济学排序
        # 2 0 1
        _indexs = [2, 0, 1]
        try:
            a_i = _indexs.index(a['question_subject'])
            b_i = _indexs.index(b['question_subject'])
        except Exception:
            return 0
        return a_i - b_i

    choice_blocks = []
    current_sm = 0
    current_questions = []
    answer_blocks = []

    for q_item in question_items:
        sm = q_item['select_mode']
        if sm <= 0:
            continue
        if sm == current_sm:
            current_questions.append(q_item)
        else:
            if current_sm == 0 or current_sm >= len(select_modes):
                pass
            else:
                title = select_modes[current_sm]
                block = {'title': title, 'questions': current_questions,
                         'mode': current_sm}
                if current_sm in (1, 6):
                    choice_blocks.append(block)
                else:
                    answer_blocks.append(block)
            current_sm = sm
            current_questions = [q_item]
    if current_sm == 0 or current_sm >= len(select_modes):
        pass
    else:
        title = select_modes[current_sm]
        block = {'title': title, 'questions': current_questions,
                 'mode': current_sm}
        if current_sm in (1, 6):
            choice_blocks.append(block)
        else:
            answer_blocks.append(block)

    #  数据处理
    question_no = 1
    rid_c = Counter('rid')
    rid_p = 'rId'
    medias = []
    answer_medias = []
    block_index = 0
    for c_block in choice_blocks:
        c_block['questions'].sort(key=cmp_to_key(_question_sort))
        c_questions = c_block["questions"]
        b_title = '%s、%s（共%s题）' % (cn_num[block_index], c_block["title"],
                                   len(c_questions))
        c_block['title'] = b_title
        for s_item in c_questions:
            _item, _medias = handle_choice_question(s_item, question_no,
                                                    rid_c,  rid_p)
            medias.extend(_medias)
            question_no += 1
        block_index += 1


    for q_block in answer_blocks:
        b_title = '%s、%s（共%s题）' % (cn_num[block_index], q_block["title"],
                                   len(q_block["questions"]))
        block_index += 1
        q_block['title'] = b_title
        q_block["questions"].sort(key=cmp_to_key(_question_sort))
        for q_item in q_block["questions"]:
            q_item["this_question_no"] = question_no
            multi_question_desc = [['%s.' % question_no]]
            for _r_item in q_item['question_desc_rich']:
                m_item = _handle_rich_desc(_r_item, rid_c, rid_p)
                medias.append(m_item)
                if not isinstance(_r_item, dict):
                    _items = _r_item.split('\n')
                    multi_question_desc[-1].append(_items[0])
                    for _sub_item in _items[1:]:
                        multi_question_desc.append([_sub_item])
                else:
                    multi_question_desc[-1].append(_r_item)

            multi_answer_rich = [[]]
            for _r_item in q_item['answer_rich']:
                m_item = _handle_rich_desc(_r_item, rid_c, rid_p)
                answer_medias.append(m_item)
                if not isinstance(_r_item, dict):
                    _items = _r_item.split('\n')
                    multi_answer_rich[-1].append(_items[0])
                    for _sub_item in _items[1:]:
                        multi_answer_rich.append([_sub_item])
                else:
                    multi_answer_rich[-1].append(_r_item)
            q_item['multi_answer_rich'] = multi_answer_rich
            q_item["multi_question_desc"] = multi_question_desc

            question_no += 1
    if answer_mode == 'alone' or answer_mode == 'alone_detail':
        alone_answers = get_alone_answers(choice_blocks, answer_blocks,
                                          answer_mode)
    else:
        alone_answers = []
    medias = [x for x in medias if x]
    answer_medias = [x for x in answer_medias if x]
    r = {'single_blocks': choice_blocks,
         'answer_blocks': answer_blocks,
         'option_mapping': OPTION_MAPPING,
         'medias': medias, 'answer_medias': answer_medias,
         'alone_answers': alone_answers}
    return r


def write_docx(save_dir, exam_name, answer_mode, question_items, select_modes,
               upload_folder):
    extension = 'docx'
    if answer_mode == 'embedded':
        extension = 'zip'
    filename = '_wildzh_export_%s.%s' % (uuid.uuid4().hex, extension)
    save_path = os.path.join(save_dir, filename)
    # copy
    temp_dir = tempfile.gettempdir()
    demo_dir = os.path.join(temp_dir, '_wildzh_%s' % uuid.uuid4().hex)
    src_dir = os.path.join(abs_dir, 'demo3')
    shutil.copytree(src_dir, demo_dir)
    media_dir = os.path.join(demo_dir, 'word', 'media')
    os.mkdir(media_dir)
    q_data = receive_data(question_items, select_modes, answer_mode)
    medias = q_data['medias']
    answer_medias = q_data['answer_medias']
    for m in medias:
        download_file(m['url'], upload_folder, media_dir, m['name'])
    if answer_mode == 'embedded':
        q_data['alone_answers'] = []
        _id = uuid.uuid4().hex
        r_name = '_wildzh_%s.docx' % _id
        ra_name = '_wildzh_%s_answer.docx' % _id
        f_path = os.path.join(temp_dir, r_name)
        fa_path = os.path.join(temp_dir, ra_name)
        write_xml(f_path, demo_dir, exam_name=exam_name,
                  show_answer=False, **q_data)

        for m in answer_medias:
            download_file(m['url'], upload_folder, media_dir, m['name'])
        write_xml(fa_path, demo_dir, exam_name=exam_name,
                  show_answer=True, **q_data)
        zip_write = zipfile.ZipFile(save_path, "w")
        zip_write.write(f_path, '%s.docx' % exam_name)
        zip_write.write(fa_path, '%s（带答案）.docx' % exam_name)
        zip_write.close()
        os.remove(f_path)
        os.remove(fa_path)
    elif answer_mode == 'alone' or answer_mode == 'alone_detail':
        for m in answer_medias:
            download_file(m['url'], upload_folder, media_dir, m['name'])
        write_xml(save_path, demo_dir, exam_name=exam_name,
                  show_answer=False, **q_data)
    else:
        q_data['alone_answers'] = []
        write_xml(save_path, demo_dir, exam_name=exam_name,
                  show_answer=False, **q_data)

    shutil.rmtree(demo_dir)
    save_name = '%s.%s' % (exam_name, extension)
    return save_path, save_name


if __name__ == "__main__":
    write_docx('b.docx', 'Test2', False, [], [], '.')

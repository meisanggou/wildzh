# !/usr/bin/env python
# coding: utf-8

from functools import cmp_to_key
import re
import os
import shutil
import tempfile
import uuid
import zipfile

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


def receive_data(question_items, select_modes, media_dir, upload_folder,
                 show_answer=False):
    def _question_sort(a, b):
        # 按照政治经济学，微观经济学，宏观经济学排序
        # 3 1 2
        _indexs = [3, 1, 2, 0]
        try:
            a_i = _indexs.index(a['question_subject'])
            b_i = _indexs.index(b['question_subject'])
        except Exception:
            return 0
        return a_i - b_i

    single_selected = []
    current_sm = 0
    current_questions = []
    answer_blocks = []

    for q_item in question_items:
        sm = q_item['select_mode']
        if sm <= 0:
            continue
        if sm == 1:
            single_selected.append(q_item)
        else:
            if sm == current_sm:
                current_questions.append(q_item)
            else:
                if current_sm == 0 or current_sm >= len(select_modes):
                    pass
                else:
                    title = select_modes[current_sm]
                    answer_blocks.append({'title': title,
                                          'questions': current_questions})
                current_sm = sm
                current_questions = [q_item]
    if current_sm == 0 or current_sm >= len(select_modes):
        pass
    else:
        title = select_modes[current_sm]
        answer_blocks.append({'title': title,
                              'questions': current_questions})
    single_selected.sort(key=cmp_to_key(_question_sort))

    #  数据处理
    question_no = 1
    rid_c = Counter('rid')
    rid_p = 'rId'
    medias = []

    def _handle_rich_desc(rd_item):
        if isinstance(rd_item, dict):
            rid = "%s%s" % (rid_p, rid_c.value)
            rd_item['rid'] = rid
            rd_item['width'] = int(rd_item['width'] * 10000)
            rd_item['height'] = int(rd_item['height'] * 10000)
            rd_item['r_index'] = rid_c.value
            r_name = '%s.%s' % (rid, rd_item['url'].rsplit('.', 1)[-1])
            rd_item['name'] = r_name
            download_file(rd_item['url'], upload_folder, media_dir, r_name)
            rid_c.plus()
            medias.append({'rid': rid, 'name': r_name})
    for s_item in single_selected:
        for _r_item in s_item['question_desc_rich']:
            _handle_rich_desc(_r_item)
        s_item['question_desc_rich'].insert(0, '%s.' % question_no)
        s_item["this_question_no"] = question_no
        question_no += 1
        max_score = -100
        right_index = -1
        max_option_len = 0
        for index in range(len(s_item["options"])):
            item = s_item["options"][index]
            o_len = 0
            _ll = []
            for dr_item in item['desc_rich']:
                if isinstance(dr_item, dict):
                    o_len += dr_item['width'] / 10
                    _handle_rich_desc(dr_item)
                else:
                    o_len += string_length(dr_item)
            item['desc_rich'].insert(0, '%s.' % OPTION_MAPPING[index])
            item['desc_rich'].extend(_ll)
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
    block_index = 0
    if single_selected:
        b_title = '%s、%s（共%s题）' % (cn_num[0], select_modes[1],
                                   len(single_selected))
        single_block = {'title':  b_title, 'questions': single_selected}
        block_index += 1
    else:
        single_block = None

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
                _handle_rich_desc(_r_item)
                if not isinstance(_r_item, dict):
                    _items = _r_item.split('\n')
                    multi_question_desc[-1].append(_items[0])
                    for _sub_item in _items[1:]:
                        multi_question_desc.append([_sub_item])
                else:
                    multi_question_desc[-1].append(_r_item)

            multi_answer_rich = [[]]
            if show_answer:
                for _r_item in q_item['answer_rich']:
                    _handle_rich_desc(_r_item)
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

    r = {'single_block': single_block,
         'answer_blocks': answer_blocks,
         'option_mapping': OPTION_MAPPING,
         'medias': medias}
    return r


def write_docx(save_path, exam_name, show_answer, question_items, select_modes,
               upload_folder):
    # copy
    temp_dir = tempfile.gettempdir()
    demo_dir = os.path.join(temp_dir, '_wildzh_%s' % uuid.uuid4().hex)
    src_dir = os.path.join(abs_dir, 'demo3')
    shutil.copytree(src_dir, demo_dir)
    media_dir = os.path.join(demo_dir, 'word', 'media')
    os.mkdir(media_dir)
    q_data = receive_data(question_items, select_modes, media_dir,
                          upload_folder, show_answer)
    if show_answer is None:
        _id = uuid.uuid4().hex
        r_name = '_wildzh_%s.docx' % _id
        ra_name = '_wildzh_%s_answer.docx' % _id
        f_path = os.path.join(temp_dir, r_name)
        fa_path = os.path.join(temp_dir, ra_name)
        write_xml(f_path, demo_dir, exam_name=exam_name,
                  show_answer=False, **q_data)
        write_xml(fa_path, demo_dir, exam_name=exam_name,
                  show_answer=True, **q_data)
        zip_write = zipfile.ZipFile(save_path, "w")
        zip_write.write(f_path, '%s.docx' % exam_name)
        zip_write.write(fa_path, '%s（带答案）.docx' % exam_name)
        zip_write.close()
        os.remove(f_path)
        os.remove(fa_path)
    else:
        write_xml(save_path, demo_dir, exam_name=exam_name,
                  show_answer=show_answer, **q_data)

    shutil.rmtree(demo_dir)
    return save_path


if __name__ == "__main__":
    write_docx('b.docx', 'Test2', False, [], [], '.')

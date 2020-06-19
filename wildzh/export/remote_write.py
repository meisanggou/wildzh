# !/usr/bin/env python
# coding: utf-8

import re
import os
import requests

from render_xml import write_xml


__author__ = 'meisa'

SERVER_EP = 'https://wild.gene.ac'
OPTION_MAPPING = ["A", "B", "C", "D"]
cn_num = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一",
          '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']
session = requests.session()
session.headers["User-Agent"] = "jyrequests"


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

    def __init__(self, name, index=0):
        self.name = name
        self._index = index

    @property
    def value(self):
        return self._index

    def plus(self):
        self._index += 1


class QuestionCache(object):
    _instance = None
    _cache = set()

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        o = object.__new__(cls)
        cls._instance = o
        return o

    def __init__(self, auto_cache=True):
        self.auto_cache = auto_cache

    def add(self, exam_no, question_no):
        self._cache.add((exam_no, question_no))

    def exist(self, exam_no, question_no):
        if (exam_no, question_no) in self._cache:
            return True
        if self.auto_cache:
            self.add(exam_no, question_no)
        return False

    @property
    def length(self):
        return len(self._cache)


ONE = False


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


def request_diff_questions(exam_no, num, select_mode=None):
    questions = []
    rate = 1
    _qc = QuestionCache()
    while len(questions) < num:
        offset = num - len(questions)
        r_num = rate * offset
        req_questions = request_questions(exam_no, r_num, select_mode)
        for item in req_questions['data']:
            exist = _qc.exist(item['exam_no'], item['question_no'])
            if not exist:
                questions.append(item)
                if len(questions) >= num:
                    break
            else:
                print(item)
    return questions


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

    def _question_sort(a, b):
        # 按照政治经济学，微观经济学，宏观经济学排序
        # 3 1 2
        _indexs = [3, 1, 2, 0]
        a_i = _indexs.index(a['question_subject'])
        b_i = _indexs.index(b['question_subject'])
        return a_i - b_i
    # 获取 60道 选择题
    single_selected = request_diff_questions(exam_no, 60, 1)
    single_selected.sort(cmp=_question_sort)

    answer_blocks = []
    # 获得 5题 名词解释
    block1 = request_diff_questions(exam_no, 5, 2)
    answer_blocks.append(dict(title=u"二、名词解释(每小题3分,共15分)", questions=block1))
    # 获得 4题 简答题
    block2 = request_diff_questions(exam_no, 4, 3)
    answer_blocks.append(dict(title=u"三、简答题(每小题5分,共20分)", questions=block2))
    # 获得 2题 计算题
    block3 = request_diff_questions(exam_no, 2, 4)
    answer_blocks.append(dict(title=u"四、计算题(70题10分,71题15分,共25分)", questions=block3))
    # 获得 2题 论述题
    block4 = request_diff_questions(exam_no, 2, 5)
    answer_blocks.append(dict(title=u"五、论述题(每小题15分,共30分)", questions=block4))

    #  数据处理
    question_no = 1
    rid_c = Counter('rid')
    rid_p = 'rIdm'
    medias = []
    exist_mf = os.listdir(media_dir)
    for item in exist_mf:
        _file = os.path.join(media_dir, item)
        os.remove(_file)

    def _handle_rich_desc(rd_item):
        if isinstance(rd_item, dict):
            rid = "%s%s" % (rid_p, rid_c.value)
            rd_item['rid'] = rid
            rd_item['width'] = int(rd_item['width'] * 10000)
            rd_item['height'] = int(rd_item['height'] * 10000)
            rd_item['r_index'] = rid_c.value
            r_name = '%s.%s' % (rid, rd_item['url'].rsplit('.', 1)[-1])
            rd_item['name'] = r_name
            download_file(rd_item['url'], media_dir, r_name)
            rid_c.plus()
            medias.append({'rid': rid, 'name': r_name})
    for s_item in single_selected:
        for _r_item in s_item['question_desc_rich']:
            _handle_rich_desc(_r_item)

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

    for q_block in answer_blocks:
        q_block["questions"].sort(cmp=_question_sort)
        for q_item in q_block["questions"]:
            q_item["this_question_no"] = question_no
            multi_question_desc = [[]]
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
    single_block = {'title':  u'一、选择题(每小题1分,共60分)',
                    'questions': single_selected}
    r = {'single_block': single_block,
         'answer_blocks': answer_blocks,
         'option_mapping': OPTION_MAPPING,
         'medias': medias}
    return r


if __name__ == "__main__":
    # q_data['single_selected'] = []
    # q_data['answer_blocks'] = []
    for num in cn_num[:1]:
        media_dir = 'demo2/word/media'
        q_data = receive_data('1570447137', media_dir)
        name = ('自测题' + num).decode('utf-8')
        write_xml(u'%s_答案.docx' % name, 'demo2', exam_name=name, show_answer=True,
                  **q_data)
        write_xml('%s.docx' % name, 'demo2', exam_name=name, clear_demo=True,
                  **q_data)
    print(QuestionCache().length)

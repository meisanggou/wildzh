# !/usr/bin/env python
# coding: utf-8
import os
import re
import requests
__author__ = 'meisa'

req = requests.session()
headers = {"User-Agent": "jyrequests"}
req.headers = headers
remote_host = "https://meisanggou.vicp.net"
# remote_host = "http://127.0.0.1:2400"


def read_file(file_path, *args):
    s_c = args
    if len(s_c) == 0:
        s_c = ["."]
    m_compile = re.compile(u"(\d+)(%s)" % "|".join(map(lambda x: re.escape(x), s_c)))

    with open(file_path, "r") as r:
        c = r.read()
        all_lines = c.split("\n")
        questions_s = []
        current_question = []
        for line in all_lines:
            s_line = line.strip().decode("utf-8")
            if len(s_line) <= 0:
                continue
            m_no = m_compile.match(s_line)
            if m_no is not None:
                questions_s.append(current_question)
                current_question = [s_line[len("".join(m_no.groups())):]]

            else:
                current_question.append(s_line)
        questions_s.append(current_question)
    return questions_s[1:]


def get_question(question_items, *args):
    s_c = args
    desc = ""
    i = 0
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
    for item in question_items[i:]:
        r_item = r_compile.sub(replace, item)
        options.extend(r_item.split("\n"))
    real_options = map(lambda x: x.strip(), options)
    real_options = filter(lambda x: len(x) > 0, real_options)
    if len(real_options) != 4:
        for r_o in real_options:
            print(r_o)
        return None
    # for r_o in real_options:
    #     print(r_o)
    return dict(desc=desc, options=real_options)


def login(user_name, password):
    url = remote_host + "/user/login/"
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
        data = dict(question_no=question_no, select_mode=0)
        data["question_desc"] = q_item["desc"].strip()
        data["options"] = map(lambda x: dict(desc=x.strip(), score=0), q_item["options"])
        data["options"][0]["score"] = 1
        data["answer"] = exam_name
        resp = req.post(url, json=data)
        print(resp.text)
        question_no += 1


if __name__ == "__main__":
    file_path = u"2015年经济学真题.txt"
    exam_name = os.path.basename(file_path).rsplit(".", 1)[0]
    error_path = file_path + ".error"
    questions = read_file(file_path, ".", u"、", u"．")
    f_questions = []
    we = open(error_path, "w")
    for item in questions:
        q_item = get_question(item, ".", u"、", u"．")
        if q_item is None:
            t_s = "\n".join(item)
            we.write(t_s.encode("utf-8") + "\n")
        else:
            f_questions.append(q_item)
        # break

    login("admin", "admin")
    exam_no = 1566699611
    no_info = req_max_no(exam_no)
    # post_questions(exam_name, exam_no, no_info["next_no"], f_questions)

    we.close()

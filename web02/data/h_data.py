# !/usr/bin/env python
# coding: utf-8
import re
import requests
__author__ = 'meisa'

req = requests.session()
headers = {"User-Agent": "jyrequests"}
req.headers = headers
remote_host = "https://meisanggou.vicp.net"

def read_file(file_path):
    with open(file_path, "r") as r:
        c = r.read()
        all_lines = c.split("\n")
        questions_s = []
        current_question = []
        for line in all_lines:
            # print(line)
            s_line = line.strip()
            if re.match("\d+", s_line) is not None:
                questions_s.append(current_question)
                current_question = [s_line]
            else:
                current_question.append(s_line)
        questions_s.append(current_question)
    return questions_s[1:]


def get_question(question_items):
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
        return "\n" + mgs[0] + u"、"
    for item in question_items[i:]:
        r_item = re.sub(u"(A|B|C|D)、", replace, item.decode("utf-8"))
        options.extend(r_item.split("\n"))
    # option_s = "\n".join(question_items[i:]).decode("utf-8")
    # print(option_s)
    # options = re.findall(u"((A|B|C|D)、[\s\S]*?)[ABCD$\n]", option_s, re.I)
    assert len(options) != 4
    # for o in options:
    #     print(o[0])


def login(user_name, password):
    url = remote_host + "/user/login/"
    data = dict(user_name=user_name, password=password, next="/exam/")
    print(url)
    response = req.post(url, json=data)
    print(response.text)


def get_questions(exam_no):
    url = remote_host + "/exam/questions/"


if __name__ == "__main__":
    questions = read_file("exam_file.txt")
    for item in questions:
        q_item = get_question(item)
        # break
    login("admin", "admin")

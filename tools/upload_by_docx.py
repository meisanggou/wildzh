# !/usr/bin/env python
# coding: utf-8

from handle_exam import handle_exam_no_answer
from handle_exam import upload_js_with_answer

__author__ = 'zhouhenglc'


if __name__ == "__main__":
    exam_no = 1567506833  # 测试包含图片
    exam_no = 1570447137  # 专升本经济学题库2
    # exam_no = 1573464937  # 英语托业
    file_path = u'D:/Project/word/app/upload/第八章 生产要素价格的决定.docx'
    handle_exam_no_answer(exam_no, file_path)
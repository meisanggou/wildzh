# !/usr/bin/env python
# coding: utf-8
import cv2
import uuid


__author__ = 'zhouhenglc'


def clip_pic(pic_file, clip_data):
    """
    :param pic_file:  文件路径
    :param clip_data:  [a, b, c, d]
    a 从距离图片左边 a开始 a为图片宽度百分比
    b 从距离图片上边 b开始 b为图片高度百分比
    c 到距离图片左边 c结束 c为图片宽度百分比
    d 到距离图片上边 d开始 d为图片高度百分比
    :return:
    """
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

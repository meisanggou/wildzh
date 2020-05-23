# !/usr/bin/env python
# coding: utf-8
import os
import Queue
import zipfile

__author__ = 'zhouhenglc'


def write_zip(target_dir, target_files=None):
    abs_target_dir = os.path.abspath(target_dir)
    all_files = []
    q = Queue.Queue()
    if target_files is None:
        q.put(abs_target_dir)
    else:
        for item in target_files:
            abs_item = os.path.abspath(os.path.join(abs_target_dir, item))
            q.put(abs_item)
    while q.empty() is False:
        p = q.get()
        if os.path.isdir(p) is True:
            for item in os.listdir(p):
                abs_item = os.path.abspath(os.path.join(p, item))
                q.put(abs_item)
        else:
            all_files.append(p)
    relative_files = []
    target_len = len(abs_target_dir) + 1
    for item in all_files:
        relative_files.append([item, item[target_len:]])
    return relative_files


def directory_to_docx(filename, dir_path):
    zip_write = zipfile.ZipFile(filename, "w")
    # ["_rels", "docProps", "word", "[Content_Types].xml"]
    zip_files = write_zip(dir_path, )
    for z_file in zip_files:
        zip_write.write(z_file[0], z_file[1])
    zip_write.close()

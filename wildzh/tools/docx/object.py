# !/usr/bin/env python
# coding: utf-8
import os
import shutil
import tempfile
import uuid
import xml.dom.minidom as minidom
import zipfile

from wildzh.tools.docx.xml_node import get_node


__author__ = 'zhouhenglc'


class DocxObject(object):

    def __init__(self, path, exit_delete=False):
        self.path = path
        self._extract_dir = None
        self._document_path = None
        self._relationships = None
        self.exit_delete = exit_delete

    @property
    def extract_dir(self):
        if self._extract_dir is None:
            self._extract_dir = self.extract_docx(self.path)
        return self._extract_dir

    @property
    def document_path(self):
        _path = os.path.join(self.extract_dir, 'word', 'document.xml')
        return _path

    @property
    def rels_path(self):
        style_path = os.path.join(self.extract_dir, 'word', '_rels',
                                  "document.xml.rels")
        return style_path

    @staticmethod
    def extract_docx(path):
        temp_dir_name = "_wildzh_%s" % uuid.uuid4().hex
        temp_dir = os.path.join(tempfile.gettempdir(), temp_dir_name)
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
        zf = zipfile.ZipFile(path)
        zf.extractall(path=temp_dir)
        return temp_dir

    def get_resource_path(self, relative_path):
        abs_path = os.path.join(self.extract_dir, "word", relative_path)
        return abs_path

    @property
    def relationships(self):
        if self._relationships is None:
            rels_dom = minidom.parse(self.rels_path)
            relationships_node = rels_dom.firstChild
            relationships = dict()
            for rs in get_node(relationships_node, "Relationship"):
                r_id = rs.getAttribute("Id")
                target = rs.getAttribute("Target")
                relationships[r_id] = self.get_resource_path(target)
            self._relationships = relationships
        return self._relationships

    def read_paragraphs(self, **kwargs):
        skip_empty = kwargs.pop('skip_empty', True)
        handle_paragraph = kwargs['handle_paragraph']
        dom = minidom.parse(self.document_path)
        root = dom.documentElement
        body = root.firstChild
        for node in body.childNodes:
            if node.nodeName != "w:p":
                continue
            p_content = handle_paragraph(node).strip()
            if len(p_content) <= 0 and skip_empty:
                continue
            yield p_content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.extract_dir:
            try:
                shutil.rmtree(self.extract_dir, ignore_errors=True)
                if self.exit_delete:
                    os.remove(self.path)
            except Exception as e:
                pass

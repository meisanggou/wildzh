# !/usr/bin/env python
# coding: utf-8
from contextlib import contextmanager
from flask import g
from flask import has_app_context
from flask_login import login_required

from flask_helper.utils.registry import DataRegistry
from flask_helper.view import View

from wildzh.db import session

__author__ = 'zhouhenglc'


DR = DataRegistry.get_instance()


def add_menu(url_prefix, menu_list):
    m_key = 'portal_menu_list'
    DR.set_default(m_key, [])
    DR.set_default('portal_menu_list.cache', {})
    cache = DR.get('portal_menu_list.cache')
    candidate_menu = []
    if isinstance(menu_list, (list, tuple)) is True:
        for item in menu_list:
            if "index" not in item:
                item["index"] = len(DR.get(m_key)) + 10
            if "url" not in item:
                item["url"] = url_prefix.rstrip('/') + "/"
            else:
                item['url'] = url_prefix + item["url"]
            if 'is_child' in item and item['is_child']:
                if item.get('sub_menu'):
                    sub_menu = cache.setdefault(item['menu_id'], [])
                    sub_menu.extend(item.get('sub_menu'))
            else:
                candidate_menu.append(item)
    elif isinstance(menu_list, dict) is True:
        if "index" not in menu_list:
            menu_list["index"] = len(DR.get(m_key)) + 10
        if "url" not in menu_list:
            menu_list["url"] = url_prefix.rstrip('/') + "/"
        if 'is_child' in menu_list and menu_list['is_child']:
            if menu_list.get('sub_menu'):
                sub_menu = cache.setdefault(menu_list['menu_id'], [])
                sub_menu.extend(menu_list.get('sub_menu'))
        else:
            candidate_menu.append(menu_list)
    for item in candidate_menu:
        for e_item in DR.get(m_key):
            if e_item['menu_id'] == item['menu_id']:
                # TODO write log
                break
        else:
            DR.append('portal_menu_list', item)
    for e_item in DR.get(m_key):
        if e_item['menu_id'] in cache:
            sub_menu = e_item.setdefault('sub_menu', [])
            sub_menu.extend(cache[e_item['menu_id']])
            del cache[e_item['menu_id']]


class Context(object):

    def __init__(self):
        self._session = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, s):
        if has_app_context():
            g.session2 = s
        self._session = s


class View2(View):

    def __init__(self, name, import_name, **kwargs):
        auth_required = kwargs.pop('auth_required', False)
        menu_list = kwargs.pop('menu_list', None)
        url_prefix = kwargs.get('url_prefix', '/')
        View.__init__(self, name, import_name, **kwargs)
        if auth_required:
            @self.before_request
            @login_required
            def before_request():
                pass
        if menu_list:
            add_menu(url_prefix, menu_list)

    @classmethod
    @contextmanager
    def view_context_func(cls):
        with session.use_session() as _session:
            context = Context()
            context.session = _session
            yield context

    def add_handler(self, handler_obj, name=None):
        if not name:
            name = self.name
        kwargs = {name: handler_obj}
        DR.update('handlers', **kwargs)

    def get_handler(self, name=None):
        if not name:
            name = self.name
        return DR.get('handlers').get(name)

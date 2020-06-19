# !/usr/bin/env python
# coding: utf-8
from flask_login import current_user, LoginManager, login_required

from flask_helper.view import View

__author__ = 'zhouhenglc'


portal_menu_list = []


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
        if menu_list is not None:
            if isinstance(menu_list, (list, tuple)) is True:
                for item in menu_list:
                    if "index" not in item:
                        item["index"] = len(portal_menu_list) + 10
                    if "url" not in item:
                        item["url"] = url_prefix + "/"
                    else:
                        item['url'] = url_prefix + item["url"]
                    portal_menu_list.append(item)
            elif isinstance(menu_list, dict) is True:
                if "index" not in menu_list:
                    menu_list["index"] = len(portal_menu_list) + 10
                if "url" not in menu_list:
                    menu_list["url"] = url_prefix + "/"
                portal_menu_list.append(menu_list)

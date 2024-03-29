# !/usr/bin/env python
# coding: utf-8
from flask import g, request, session, make_response

from flask_helper.flask_hook import FlaskHook

from wildzh.utils import registry
from wildzh.web02 import login_manager


__author__ = 'zhouhenglc'


class TokenHook(FlaskHook):
    priority = 190

    def __init__(self, app):
        FlaskHook.__init__(self, app)
        self.auth_header = 'X-OAuth-Token'
        self.url_token_header = 'X-Url-Token'

    def before_request(self):
        login_manager = getattr(self.app, 'login_manager', None)
        if not login_manager:
            self.log.warning('no set login_manager, token hook not work')
            return
        auth_data = request.headers.get(self.auth_header)
        if auth_data is None:
            key = request.headers.get(self.url_token_header)
            if not key:
                return
            auth_data = request.args.get(key)
            if not auth_data:
                return
        v_r, data = registry.notify_callback('hook', 'verify_token', self,
                                             token=auth_data)
        if v_r is True:
            g.token = data
            session['_user_id'] = data['user_no']
            session['role'] = data['extra_data']['user_role']
            g.user_role = data['extra_data']['user_role']
            if login_manager.session_protection == 'strong':
                ident = login_manager._session_identifier_generator()
                session['_id'] = ident
            login_manager._load_user()

        else:
            error = data.get('error', '')
            detail = data.get('detail', '')
            self.log.info('verify token fail, error: %s, detail: %s',
                          error, detail)
            return make_response(error, 401)

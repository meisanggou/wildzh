# !/usr/bin/env python
# coding: utf-8
import os

from wildzh.utils.config import ConfigLoader

__author__ = 'zhouhenglc'

script_dir = os.path.abspath(os.path.dirname(__file__))
etc_dir = os.path.abspath(os.path.join(script_dir, '..', 'etc'))

_LOADED = {}
_ETC_DIRS = list()
if os.environ.get('ETCPATH'):
    _e_path = os.path.abspath(os.environ['ETCPATH'])
    _ETC_DIRS.append(_e_path)
if etc_dir not in _ETC_DIRS:
    _ETC_DIRS.append(etc_dir)


def _load_config_paths(name):
    if not name.endswith('conf'):
        name = '%s.conf' % name
    return [os.path.join(d, name) for d in _ETC_DIRS]


def load_mysql_cfg():
    key = 'mysql'
    if key in _LOADED:
        return _LOADED[key]
    cl = ConfigLoader(*_load_config_paths('mysql_app'))
    section = 'db_basic'
    db_host = cl.get(section, 'host')
    db_port = cl.get(section, 'port')
    db_name = cl.get(section, 'name')
    u_section = '%s_user' % section
    db_user = cl.get(u_section, 'user')
    db_password = cl.get(u_section, 'password')
    ru_section = '%s_read_user' % section
    if cl.has_section(ru_section):
        db_ro_user = cl.get(ru_section, 'user')
        db_ro_password = cl.get(ru_section, 'password')
    else:
        db_ro_user = db_user
        db_ro_password = db_password
    cfg = {'db_host': db_host, 'db_port': db_port, 'db_name': db_name,
           'db_user': db_user, 'db_password': db_password,
           'db_ro_user': db_ro_user, 'db_ro_password': db_ro_password}
    _LOADED[key] = cfg
    return _LOADED[key]

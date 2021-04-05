# !/usr/bin/env python
# coding: utf-8
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wildzh.config import load_mysql_cfg

__author__ = 'zhouhenglc'


_ENGINE = None


def get_conn_url(**kwargs):
    d_kwargs = load_mysql_cfg()
    d_kwargs.update(kwargs)
    conn_url = 'mysql+pymysql://%(db_user)s:%(db_password)s@%(db_host)s:' \
               '%(db_port)s/%(db_name)s?charset=utf8' % d_kwargs
    return conn_url


def get_engine(**options):
    global _ENGINE
    if not _ENGINE:
        conn_url = get_conn_url()
        _options = {'pool_size': 10, 'pool_timeout': 10, 'max_overflow': 20,
                    'pool_recycle': 3600}
        _options.update(options)
        _ENGINE = create_engine(conn_url, **_options)
    return _ENGINE


def reload_engine(**options):
    global _ENGINE
    _ENGINE = None
    return get_engine(**options)


def get_session():
    session = sessionmaker(bind=get_engine())()
    return session


@contextmanager
def use_session():
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

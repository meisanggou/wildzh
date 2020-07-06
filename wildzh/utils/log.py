# !/usr/bin/env python
# coding: utf-8
import logging
from logging import Formatter, StreamHandler
from logging.handlers import WatchedFileHandler

import os
import sys

from zh_config import log_file

__author__ = 'zhouhenglc'

LOG_LEVEL = logging.INFO
LOG_FILE = log_file

fmt = Formatter('%(asctime)s:%(levelname)s:%(message)s')

file_handler = WatchedFileHandler(LOG_FILE)
file_handler.level = logging.DEBUG
file_handler.setFormatter(fmt)

console_handle = StreamHandler(sys.stdout)
console_handle.level = logging.DEBUG
console_handle.setFormatter(fmt)


def set_logger_as_root(name):
    logger = logging.getLogger(name)
    # if not os.environ.get('LOG_NO_FILE'):
    #     logger.addHandler(file_handler)
    # if os.environ.get('LOG_CONSOLE'):
    logger.addHandler(console_handle)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False
    return logger


def getLogger(name='wildzh'):
    logger = logging.getLogger(name)
    return logger


set_logger_as_root(None)
set_logger_as_root('wildzh')

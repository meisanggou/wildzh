# !/usr/bin/env python
# coding: utf-8
import configparser
import os

__author__ = 'zhouhenglc'


class ConfigLoader(object):

    def __init__(self, *paths):
        self._loaded = []
        self._cache = {}
        for _path in paths:
            if not os.path.exists(_path):
                continue
            _config = configparser.ConfigParser()
            _config.read(_path)
            self._loaded.append(_config)

    def has_section(self, section_name):
        if section_name in self._cache:
            if self._cache[section_name] is None:
                return False
            return True
        for loaded_cfg in self._loaded:
            if loaded_cfg.has_section(section_name):
                self._cache[section_name] = loaded_cfg
                return True
        else:
            self._cache[section_name] = None
            return False

    def has_option(self, section, option):
        key = '%s_%s' % (section, option)
        if key in self._cache:
            return True
        if key.upper() in os.environ:
            return True
        if self.has_section(section) is False:
            return False
        cfg = self._cache[section]
        return cfg.has_section(section, option)

    def get(self, section, option):
        key = '%s_%s' % (section, option)
        if key in self._cache:
            return self._cache[key]
        if key.upper() in os.environ:
            return os.environ[key.upper()]
        if self.has_section(section) is False:
            return None
        cfg = self._cache[section]
        return cfg.get(section, option)

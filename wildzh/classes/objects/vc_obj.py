# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


class VCheckResult(object):
    max_freq = 1

    def __init__(self, freq):
        self.freq = freq

    @property
    def result(self):
        return self.freq < self.max_freq

#! /usr/bin/env python
# coding: utf-8
__author__ = 'ZhouHeng'


class IPManager(object):

    def __init__(self):
        self.ip_1a = 256
        self.ip_2a = self.ip_1a * self.ip_1a
        self.ip_3a = self.ip_1a * self.ip_2a
        self.ip_4a = self.ip_1a * self.ip_3a

    def ip_value_str(self, ip_str=None, ip_value=None):
        if ip_str is not None:
            ip_s = ip_str.split(".")
            ip = int(ip_s[0]) * self.ip_3a + int(ip_s[1]) * self.ip_2a + int(ip_s[2]) * self.ip_1a + int(ip_s[3])
            return ip
        if ip_value is not None:
            ip_1 = ip_value / self.ip_3a
            ip_value = ip_value % self.ip_3a
            ip_2 = ip_value / self.ip_2a
            ip_value = ip_value % self.ip_2a
            ip_3 = ip_value / self.ip_1a
            ip_4 = ip_value % self.ip_1a
            ip_str = "%s.%s.%s.%s" % (ip_1, ip_2, ip_3, ip_4)
            return ip_str
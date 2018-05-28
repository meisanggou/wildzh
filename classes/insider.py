# !/usr/bin/env python
# coding: utf-8

import time
from mysqldb_rich.db2 import DB

__author__ = 'meisa'

# 2018-05-28 00:30:00 in UTC
EPOCH = 1527467400


class Insider(object):

    def __init__(self):
        pass

    @staticmethod
    def to_hex(number, z_width=8):
        hex_number = hex(number).lstrip("0x").rstrip("L").zfill(z_width).upper()
        return hex_number

    @staticmethod
    def get_timestamp():
        return int(time.time() - EPOCH)

    @staticmethod
    def create_billing_no(user_no, project_no):
        """

        :param user_no: int11
        :param project_no:  int11
        :return billing_no: timestamp(8) + user_no(8) + project_no(8) 16
        """
        print(Insider.get_timestamp())
        hex_time = Insider.to_hex(Insider.get_timestamp())
        hex_user_no = Insider.to_hex(user_no)
        hex_project_no = Insider.to_hex(project_no)
        b_no = "%s%s%s" % (hex_time, hex_user_no, hex_project_no)
        return b_no

if __name__ == "__main__":
    Insider.create_billing_no(1, 3)

# !/usr/bin/env python
# coding: utf-8
import json
import sys

from mysqldb_rich.db2 import DB
from zh_config import db_conf_path

__author__ = 'zhouhenglc'


def get_vc_user_billing():
    cols = ['user_no', 'billing_no', 'amount']
    t = 'vc_user_billing'
    db = DB(db_conf_path)
    items = db.execute_select(t, cols=cols)
    u_billings = {}
    for item in items:
        bs = u_billings.setdefault(item['user_no'], [])
        bs.append(item)
    for user_no, billings in u_billings.items():
        billings.sort(key=lambda x: x['billing_no'])
        sys_balance = 0
        for b in billings:
            sys_balance += b['amount']
            where_value = {'user_no': user_no, 'billing_no': b['billing_no']}
            db.execute_update(t, update_value={'sys_balance': sys_balance},
                              where_value=where_value)


if __name__ == '__main__':
    get_vc_user_billing()
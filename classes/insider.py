# !/usr/bin/env python
# coding: utf-8

import time
from mysqldb_rich.db2 import DB
from function import generate_qr

__author__ = 'meisa'

# 2018-05-28 00:30:00 in UTC
EPOCH = 1527467400


class Insider(object):

    def __init__(self, conf_path):
        self.db = DB(conf_path)

        self.t_p = "insider_project"
        self.t_pm = "insider_project_member"
        self.t_mb = "insider_member_billing"
        self.t_pb = "insider_project_billing"
        self.t_b = "insider_billing"
        pass

    @staticmethod
    def to_hex(number, z_width=8):
        hex_number = "%x" % number
        hex_number = hex_number.zfill(z_width).upper()
        return hex_number

    @staticmethod
    def to_decimal(hex_number):
        number = int(hex_number, 16)
        return number

    @staticmethod
    def get_timestamp():
        return int(time.time() - EPOCH)

    @property
    def add_time(self):
        return int(time.time())

    @staticmethod
    def create_billing_no(user_no, project_no):
        """

        :param user_no: int11
        :param project_no:  int11
        :return billing_no: timestamp(8) + user_no(8) + project_no(8)
        """
        hex_time = Insider.to_hex(Insider.get_timestamp())
        hex_user_no = Insider.to_hex(user_no)
        hex_project_no = Insider.to_hex(project_no)
        b_no = "%s%s%s" % (hex_time, hex_user_no, hex_project_no)
        return b_no

    @staticmethod
    def split_billing_no(b_no):
        """

        :param b_no: str24
        :return: (time, user_no, project_no)
        """
        project_no = Insider.to_decimal(b_no[-8:])
        user_no = Insider.to_decimal(b_no[-16:-8])
        timestamp = Insider.to_decimal(b_no[:-16])
        return timestamp, user_no, project_no

    def _insert_project(self, user_no, project_name=None):
        kwargs = dict(owner=user_no, project_name=project_name, add_time=self.add_time)
        l = self.db.execute_insert(self.t_p, kwargs=kwargs)
        return l

    def _insert_project_member(self, project_no, user_no, role=64):
        kwargs = dict(project_no=project_no, member_no=user_no, role=role, add_time=self.add_time)
        l = self.db.execute_insert(self.t_pm, kwargs=kwargs)
        return l

    def _insert_sys_billing(self, b_no, amount):
        kwargs = dict(billing_no=b_no, amount=amount, add_time=self.add_time)
        l = self.db.execute_insert(self.t_b, kwargs=kwargs, ignore=True)
        return l

    def _insert_member_billing(self, user_no, b_no, intention, amount, yue, zs_yue, remark):
        kwargs = dict(member_no=user_no, billing_no=b_no, amount=amount, yue=yue, zs_yue=zs_yue, intention=intention,
                      remark=remark, add_time=self.add_time)
        l = self.db.execute_insert(self.t_mb, kwargs=kwargs, ignore=True)
        return l

    def _insert_project_billing(self, project_no, b_no, intention, amount, remark):
        kwargs = dict(project_no=project_no, billing_no=b_no, amount=amount, intention=intention, remark=remark,
                      add_time=self.add_time)
        l = self.db.execute_insert(self.t_pb, kwargs=kwargs, ignore=True)
        return l

    def _update_project_member(self, project_no, user_no, **update_value):
        where_value = dict(project_no=project_no, member_no=user_no)
        l = self.db.execute_update(self.t_pm, where_value=where_value, update_value=update_value)
        return l

    def _select_project(self, project_no=None, owner=None):
        cols = ["project_no", "project_name", "owner", "add_time"]
        where_value = dict()
        if project_no is not None:
            where_value["project_no"] = project_no
        if owner is not None:
            where_value["owner"] = owner
        elif project_no is None:
            return []
        items = self.db.execute_select(self.t_p, where_value=where_value, cols=cols)
        return items

    def _select_member(self, project_no, member_no=None, lock=False):
        where_value = dict(project_no=project_no)
        if member_no is not None:
            where_value["member_no"] = member_no
        cols = ["project_no", "member_no", "role", "yue", "zs_yue", "add_time"]
        if lock is True:
            items = self.db.execute_select_with_lock(self.t_pm, cols=cols, where_value=where_value)
        else:
            items = self.db.execute_select(self.t_pm, cols=cols, where_value=where_value)
        return items

    def new_project(self, user_no, project_name=None, silently_continue=False):
        items = self._select_project(owner=user_no)
        if len(items) >= 1:
            if silently_continue is True:
                return True, items[-1]
            return False, "Exist"
        l = self._insert_project(user_no, project_name)
        if l <= 0:
            return False, "Internal Error 01"
        items = self._select_project(owner=user_no)
        if len(items) <= 0:
            return False, "Internal Error 02"
        items.reverse()
        for item in items:
            if item["project_name"] == project_name:
                return True, item
        if silently_continue is True:
            return True, items[-1]
        return False, "Internal Error 03"

    def new_pay(self, project_no, user_no, intention, amount, remark, auto_join=True):
        try:
            self.db.start_transaction()
            items = self._select_member(project_no, member_no=user_no, lock=True)
            if len(items) <= 0:
                self.db.end_transaction(fail=True)
                if auto_join is False:
                    return False, "Internal Error"
                self._insert_project_member(project_no, user_no)
                return self.new_pay(project_no, user_no, intention, amount, remark, auto_join=False)
            yue_item = items[0]
            if intention > 100:
                # 检查余额
                if yue_item["yue"] + yue_item["zs_yue"] < amount:
                    self.db.end_transaction(fail=True)
                    return False, "credit not enough"
            b_no = self.create_billing_no(user_no, project_no)
            # 创建账单
            l = self._insert_sys_billing(b_no, amount)
            if l <= 0:
                self.db.end_transaction(fail=True)
                return False, "Please Try Again"
            # 执行扣费 或者增加余额
            if intention > 100:
                if yue_item["yue"] >= amount:
                    zs_yue = yue_item["zs_yue"]
                    yue = yue_item["yue"] - amount
                else:
                    zs_yue = yue_item["zs_yue"] + yue_item["yue"] - amount
                    yue = 0
            elif intention < 50:
                zs_yue = yue_item["zs_yue"]
                yue = yue_item["yue"] + amount
            else:
                zs_yue = yue_item["zs_yue"] + amount
                yue = yue_item["yue"]
            self._update_project_member(project_no, user_no, yue=yue, zs_yue=zs_yue)
            # 查询扣费结果
            items = self._select_member(project_no, member_no=user_no)
            if len(items) <= 0:
                self.db.end_transaction(fail=True)
                return False, "Internal Error 01"
            n_yue_item = items[0]
            if n_yue_item["yue"] != yue or n_yue_item["zs_yue"] != zs_yue:
                self.db.end_transaction(fail=True)
                return False, "Internal Error 02"
            # 计入个人账单
            l = self._insert_member_billing(user_no, b_no, intention, amount, yue, zs_yue, remark)
            if l <= 0:
                self.db.end_transaction(fail=True)
                return False, "Internal Error 03"
            # 计入项目账单
            l = self._insert_project_billing(project_no, b_no, intention, amount, remark)
            if l <= 0:
                self.db.end_transaction(fail=True)
                return False, "Internal Error 04"
            self.db.end_transaction()
            n_yue_item["amount"] = amount
            return True, n_yue_item
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            self.db.end_transaction(fail=True)
            return False, "Internal Error 99"

    def select_my_project(self, user_no):
        return self._select_project(owner=user_no)

    def select_project(self, project_no=None, owner=None):
        return self._select_project(project_no, owner)

    def select_member(self, project_no, member_no=None):
        items = self._select_member(project_no, member_no)
        return items

    def create_project_qr(self, project_no, save_path):
        generate_qr(project_no, save_path)

    def verify_billing_no(self):
        cols = ["billing_no", "amount"]
        items = self.db.execute_select(self.t_b, cols=cols)
        for item in items:
            b_no = item["billing_no"]
            timestamp, user_no, project_no = self.split_billing_no(b_no)
            where_value = dict(member_no=user_no)
            where_value.update(item)
            s_items = self.db.execute_select(self.t_mb, cols=cols, where_value=where_value)
            if len(s_items) != 1:
                raise RuntimeError("Not Found %s in member billing" % b_no)
            where_value2 = dict(project_no=project_no)
            where_value2.update(item)
            s_items = self.db.execute_select(self.t_pb, cols=cols, where_value=where_value2, package=False)
            if len(s_items) != 1:
                raise RuntimeError("Not Found %s in project billing" % b_no)

    def verify(self):
        self.verify_billing_no()

    def _clear(self):
        tables = [self.t_p, self.t_pm, self.t_mb, self.t_pb, self.t_b]
        for table in tables:
            self.db.execute("DELETE FROM %s;" % table)

if __name__ == "__main__":
    from zh_config import db_conf_path
    import threading
    insider_man = Insider(db_conf_path)
    insider_man.new_project(1, project_name="wildzh", silently_continue=True)
    def pay(project_no):
        import random
        w = random.randint(1, 200)
        a = random.randint(10, 19)
        exec_r, data = insider_man.new_pay(project_no, 1, w, a, "")
        if exec_r is False:
            print(data)
    ts = []
    for i in range(5):
        t1 = threading.Thread(target=pay, args=(i + 1, ))
        t1.start()
        ts.append(t1)
    for t in ts:
        t.join()
    insider_man.verify()

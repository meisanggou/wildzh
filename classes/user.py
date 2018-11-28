# !/usr/bin/env python
# coding: utf-8

import os
import re
import time
import base64
import requests
import hashlib
import socket
import string
import random
import struct
from Crypto.Cipher import AES

from werkzeug.security import generate_password_hash, check_password_hash
from mysqldb_rich.db2 import DB
from function import generate_qr

__author__ = 'meisa'


class EncryptActor(object):
    def __init__(self, aes_key=None, actor_id=None):
        if aes_key is None or len(aes_key) != 32:
            self.aes_encode_key = "TWFNaW5nWmhhbmc2MjNJc015V2lmZUJ5V2lsZFpIMTU="
            self.aes_key = base64.b64decode(self.aes_encode_key)
        else:
            self.aes_key = aes_key
        if isinstance(actor_id, basestring) is False:
            self._id = "wild_zh"
        else:
            self._id = actor_id

    @staticmethod
    def random_str():
        """ 随机生成16位字符串
        @return: 16位字符串
        """
        rule = string.letters + string.digits
        c_list = random.sample(rule, 16)
        return "".join(c_list)

        # 解密加密数据

    def decrypt_msg(self, msg):
        try:
            key = self.aes_key
            crypt_actor = AES.new(key, AES.MODE_CBC, key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text = crypt_actor.decrypt(base64.b64decode(msg))
        except Exception, e:
            print(e)
            return ""
        try:
            pad = ord(plain_text[-1])
            # 去掉补位字符串
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack("I", content[: 4])[0])
            xml_content = content[4: xml_len + 4]
            from_app_id = content[xml_len + 4:]
        except Exception, e:
            print(e.args)
            return ""
        if from_app_id != self._id:
            return ""
        return xml_content

    def encrypt_msg(self, msg):
        msg = unicode(msg)
        # 16位随机字符串添加到明文开头
        text = self.random_str() + struct.pack("I", socket.htonl(len(msg))) + msg + self._id
        # 使用自定义的填充方式对明文进行补位填充
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = 32 - (text_length % 32)
        if amount_to_pad == 0:
            amount_to_pad = 32
        # 获得补位所用的字符
        pad = chr(amount_to_pad)
        text += pad * amount_to_pad
        # 加密
        crypt_actor = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        try:
            cipher_text = crypt_actor.encrypt(text)
            # 使用BASE64对加密后的字符串进行编码
            return base64.b64encode(cipher_text)
        except Exception, e:
            print(e.args)
            return ""


class User(object):
    _salt_password = "msg_zh2018"

    @staticmethod
    def _md5_hash(s):
        m = hashlib.md5()
        if isinstance(s, unicode) is True:
            s = s.encode("utf-8")
        m.update(s)
        return m.hexdigest()

    @staticmethod
    def _md5_hash_password(user_name, password):
        md5_password = User._md5_hash(user_name + password + user_name)
        return (md5_password + User._salt_password).upper()

    @staticmethod
    def _password_check(password, db_password, user_name):
        if db_password is None:
            return False  # 密码为空 无限期禁止登录
        if len(password) <= 20:
            if check_password_hash(db_password, User._md5_hash_password(user_name, password)) is True:
                return True
        return False

    def __init__(self, db_conf_path, upload_folder=None):
        self.encrypt = EncryptActor()
        self.db = DB(conf_path=db_conf_path)
        self.t = "sys_user"
        if upload_folder is not None:
            self.user_folder = os.path.join(upload_folder, "user")
            if os.path.exists(self.user_folder) is False:
                os.makedirs(self.user_folder)
        else:
            self.user_folder = None

    # 插入用户注册数据
    def insert_user(self, user_name=None, password=None, tel=None, nick_name=None, email=None, wx_id=None, creator=None,
                    role=1):
        add_time = int(time.time())
        kwargs = dict(user_name=user_name, password=password, tel=tel, nick_name=nick_name, email=email, wx_id=wx_id,
                      creator=creator, add_time=add_time, role=role)
        if password is not None:
            kwargs["password"] = generate_password_hash(self._md5_hash_password(user_name, password))
        l = self.db.execute_insert(self.t, kwargs=kwargs, ignore=True)
        return l

    def update_password(self, user_name, new_password):
        en_password = generate_password_hash(self._md5_hash_password(user_name, new_password))
        update_value = {"password": en_password}
        result = self.db.execute_update(self.t, update_value=update_value, where_value={"user_name": user_name})
        return result

    def _update_user(self, user_no, **update_value):
        allow_keys = ["nick_name", "avatar_url"]
        for key in update_value:
            if key not in allow_keys:
                del update_value[key]
        l = self.db.execute_update(self.t, update_value=update_value, where_value=dict(user_no=user_no))
        return l

    # 验证auth是否存在 包括 account tel alias wx_id
    def verify_user_exist(self, **kwargs):
        cols = ["user_no", "user_name", "tel", "email", "wx_id", "role", "nick_name", "avatar_url"]
        if kwargs.pop("need_password", None) is not None:
            cols.append("password")
        db_items = self.db.execute_select(self.t, where_value=kwargs, cols=cols, package=True)
        return db_items

    def new_user(self, user_name, password=None, nick_name=None, creator=None, role=1):
        items = self.verify_user_exist(user_name=user_name)
        if len(items) > 0:
            return False, u"用户名已存在"

        if nick_name is None:
            nick_name = user_name
        self.insert_user(user_name, password, nick_name=nick_name, creator=creator, role=role)
        return True, dict(user_name=user_name)

    def new_wx_user(self, wx_id):
        self.insert_user(wx_id=wx_id)
        items = self.verify_user_exist(wx_id=wx_id)
        if len(items) <= 0:
            return None
        return items[0]

    def user_confirm(self, password, user_no=None, user_name=None, email=None, tel=None, user=None):
        if user_no is not None:
            where_value = dict(user_no=user_no)
        elif user_name is not None:
            where_value = dict(user_name=user_name)
        elif email is not None:
            where_value = {"email": email}
        elif tel is not None:
            where_value = {"tel": tel}
        elif user is not None:
            if re.match(r"\d{1,10}$", user) is not None:
                where_value = dict(user_no=user)
            elif re.match(r"1\d{10}$", user) is not None:
                where_value = {"tel": user}
            elif re.match(r"\S+@\s+$", user) is not None:
                where_value = dict(email=user)
            else:
                where_value = dict(user_name=user)
        else:
            return -3, None
        where_value["need_password"] = True
        db_items = self.verify_user_exist(**where_value)
        if len(db_items) <= 0:
            return -2, None
        user_item = db_items[0]
        account = user_item["user_name"]
        db_password = user_item["password"]
        if self._password_check(password, db_password, account) is False:
            return -1, None
        del user_item["password"]
        return 0, user_item

    def generate_user_qr(self, user_no):
        if self.user_folder is None:
            return False
        avatar_path = os.path.join(self.user_folder, "%s_avatar.png" % user_no)
        qr_path = os.path.join(self.user_folder, "%s_qr.png" % user_no)
        if os.path.exists(avatar_path) is False:
            avatar_path = None
        generate_qr(self.encrypt.encrypt_msg(user_no), qr_path, avatar_path)
        return True

    def update_info(self, user_no, **kwargs):
        if "avatar_url" in kwargs:
            if kwargs["avatar_url"].startswith("http") and self.user_folder is not None:
                try:
                    resp = requests.get(kwargs["avatar_url"])
                    if resp.status_code != 200:
                        return False
                    avatar_path = os.path.join(self.user_folder, "%s_avatar.png" % user_no)
                    with open(avatar_path, "wb") as wa:
                        wa.write(resp.content)
                    self.generate_user_qr(user_no)
                except Exception as e:
                    return False
        l = self._update_user(user_no, **kwargs)
        return l

    def get_multi_nick_name(self, user_list):
        cols = ["user_no", "nick_name", "avatar_url"]
        user_list = set(user_list)
        items = self.db.execute_multi_select(self.t, where_value=dict(user_no=user_list), cols=cols)
        return items

    def my_qc_code(self, user_no):
        return self.user_folder, "%s_qr.png" % user_no

    def who_i_am(self, user_no, timeout):
        c = int(time.time() + timeout)
        d_c = "%s|%s" % (user_no, c)
        e_c = self.encrypt.encrypt_msg(d_c)
        return e_c

    def who_is(self, en_user):
        d_c = self.encrypt.decrypt_msg(en_user)
        m_r = re.match(r"^(\d+)\|(\d+)$", d_c)
        if m_r is None:
            return None
        user_no = int(m_r.groups()[0])
        timeout = int(m_r.groups()[1])
        if timeout < int(time.time()):
            return None
        return user_no

    def who_is_he(self, en_user):
        d_c = self.encrypt.decrypt_msg(en_user)
        m_r = re.match(r"^(\d+)$", d_c)
        if m_r is None:
            return None
        user_no = int(m_r.groups()[0])
        return user_no

if __name__ == "__main__":
    # import os
    import sys
    # script_dir = os.path.abspath(os.path.dirname(__file__))
    # sys.path.append(script_dir)
    from zh_config import db_conf_path
    um = User(db_conf_path)
    if len(sys.argv) >= 3:
        u = sys.argv[1]
        p = sys.argv[2]
    else:
        u = p = "admin"
    r, item = um.new_user(u, password=p)
    # if r is False:
    #     print("update password")
    #     um.update_password(u, p)
    # e = EncryptActor()
    # s = e.encrypt_msg("this is a message")
    # print(s)
    # ds = e.decrypt_msg("F36QT3Zse4Zr9bSVAn9wjd9+LJDEc8w/GPTulTbGY/4CcUvRnm04+3n8hjsk4WlZKlU0MuaOb2qhUGr7A182pA==")
    # print(ds)
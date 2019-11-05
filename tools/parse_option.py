# !/usr/bin/env python
# coding: utf-8

import re
import sys


def replace_special_space(s):
    for c in (u"\u3000", u"\xa0"):
        s = s.replace(c, " ")
    # for c in (u"\u6bb5", ):
    #     s = s.replace(c, "\n")
    return s


test_cases = [
    u"""A.既定资源的配置      B.资源总量的决定
    C.如何实现充分就业    D.国民收入的决定
""",
 u"""A.既定资源的配置      B资源总量的决定
    C.如何实现充分就业    D.国民收入的决定
""",
 u"""A.既定资源的配置      ;B.资源总量的决定
    C.如何实现充分就业    D.国民收入的决定
""",
]


class ParseOptions(object):
    option_prefix = ["A", "B", "C", "D"]
    following_chars = [".", u"、", u"．"]
    e_follow_chars = [re.escape(fc) for fc in following_chars]

    def __init__(self):
        self.A = ""
        self.B = ""
        self.C = ""
        self.D = ""
        self._o_compile = None

    @property
    def o_compile(self):
        if self._o_compile:
            return self._o_compile
        jr_chars = "|".join(self.e_follow_chars)
        self._o_compile = re.compile(u"(?:^|\\s)([ABCD])(?:%s)" % jr_chars)
        return self._o_compile

    def split_special_option(self, option_key, s):
        s_compile = re.compile("\\s%s(?:%s)" % (option_key, "|".join(
            self.e_follow_chars)))
        s_r = s_compile.split(s)
        if (len(s_r)) == 2:
            return True, s_r
        # 有些选项 A B C D后面没有点
        s_compile2 = re.compile("\\s%s" % (option_key, ))
        s_r2 = s_compile2.split(s)
        if len(s_r2) == 2:
            return True, s_r2
        # 有些选项 A B C D前面有一些符号 例如; 或者选项紧挨着， 但是后面有顿号 点之类
        s_compile3 = re.compile("%s(?:%s)" % (option_key, "|".join(
            self.e_follow_chars)))
        s_r3 = s_compile3.split(s)
        if len(s_r3) == 2:
            return True, s_r3
        # 有些选项 A B C D前面有一些符号 非中文 例如; 或者选项紧挨着， 后面也无分隔符
        s_compile4 = re.compile("%s" % (option_key, ))
        s_r4 = s_compile4.split(s)
        if len(s_r4) == 2:
            return True, s_r4
        return False, "未拆分成功"

    def verify_split_r(self, l):
        nl = [s for s in l if s.strip()]

        # 有可能A选项就不是标准格式
        if nl[0] != "A":
            prefix = nl[0]
            nl = nl[1:]
        else:
            prefix = ""
        # 拆分后长度应该是偶数
        len_nl = len(nl)
        if len_nl % 2 != 0:
            return False, "拆分后不是偶数"
        # 拆分后应该不超过8
        if len(nl) > 8:
            return False, "拆分后选项超过4个"

        kp = dict()
        for i in range(0, len_nl, 2):
            if nl[i] not in self.option_prefix:
                return False, "选项KEY不正确 理论上不应该出现的"
            kp[nl[i]] = nl[i + 1]
        # 判断每个选项A B C D是否存在
        for o_index in range(len(self.option_prefix)):
            op = self.option_prefix[o_index]
            if op not in kp.keys():
                # 选项不存在，可能包含在前一个选项里
                p_index = o_index - 1
                if p_index < 0:
                    s_result, pv_values = self.split_special_option(op, prefix)
                    if s_result is False:
                        return False, "有不存在的选项：%s" % op
                else:
                    p_p = self.option_prefix[p_index]
                    s_result, pv_values = self.split_special_option(op, kp[p_p])
                    if s_result is False:
                        return False, "有不存在的选项：%s" % op
                    kp[p_p] = pv_values[0]
                kp[op] = pv_values[1]
        self.A = kp["A"].strip()
        self.B = kp["B"].strip()
        self.C = kp["C"].strip()
        self.D = kp["D"].strip()
        return True, "success"

    def parse(self, data):
        if isinstance(data, (list, tuple)):
            s = "\n".join(data)
        else:
            s = data
        s = replace_special_space(s)
        r = self.o_compile.split(s)
        v_result, data = self.verify_split_r(r)
        if v_result is False:
            sys.stderr.write(s)
            raise RuntimeError(data)

    def to_list(self):
        return [self.A, self.B, self.C, self.D]

    @classmethod
    def test(cls, case_name, s):
        po = cls()
        print(case_name)
        po.parse(s)

    @classmethod
    def test_case1(cls):
        case_name = "测试有的选项紧挨前一个选项，而且后面没有分隔符"
        s =  u"""A.既定资源的配置B资源总量的决定
            C.如何实现充分就业    D.国民收入的决定
        """
        cls.test(case_name, s)

    @classmethod
    def test_case2(cls):
        case_name = "测试 A后面没有分隔符"
        s = u"""A既定资源的配置B资源总量的决定
                C.如何实现充分就业    D.国民收入的决定
            """
        cls.test(case_name, s)

    @classmethod
    def test_all(cls):
        cls.test_case1()
        cls.test_case2()


if __name__ == "__main__":
    ParseOptions.test_all()

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


class Option(object):

    def __init__(self, desc, score=0):
        self.desc = desc.strip()
        self.score = score

    def to_dict(self):
        return dict(desc=self.desc, score=self.score)


class ListOption(object):

    def __init__(self, option_prefix=None):
        if option_prefix:
            self.option_prefix = option_prefix
        else:
            self.option_prefix = ["A", "B", "C", "D", "E", "F"]
        for op in self.option_prefix:
            setattr(self, "_%s" % op, None)

    def _to_list(self):
        return [getattr(self, op) for op in self.option_prefix]

    def option_list(self):
        return [v for v in self._to_list() if v]

    def to_list(self):
        l_options = [v.to_dict()
                     for v in self.option_list()]
        return l_options

    def __iter__(self):
        for op in self._to_list():
            if op:
                yield op

    def __getattribute__(self, item):
        if len(item) != 1:
            return object.__getattribute__(self, item)
        if item in self.option_prefix:
            return object.__getattribute__(self, "_%s" % item)
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if len(key) != 1:
            return object.__setattr__(self, key, value)
        if key in self.option_prefix:
            _key = "_%s" % key
            _value = getattr(self, _key)
            if isinstance(value, Option):
                _value = value
            else:
                if _value:
                    _value.desc = value
                else:
                    _value = Option(value)
            object.__setattr__(self, _key, _value)
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        print(self.to_list())
        return self.to_list().__str__()


class ParseOptions(object):
    option_prefix = ["A", "B", "C", "D", "E", "F"]
    following_chars = [".", u"、", u"．"]
    e_follow_chars = [re.escape(fc) for fc in following_chars]

    def __init__(self):
        self._o_compile = None

    @property
    def o_compile(self):
        if self._o_compile:
            return self._o_compile
        jr_chars = "|".join(self.e_follow_chars)
        self._o_compile = re.compile(r"(?:^|\s)\(?\s*([ABCD])\s*\)?(?:%s)" % jr_chars)
        return self._o_compile

    def split_special_option(self, option_key, s):
        # 选项可能是 (A)
        s_compile = re.compile(r"\(\s*%s\s*\)" % (option_key,))
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
        return False, u"未拆分成功"

    def verify_split_r(self, l):
        nl = [s for s in l if s.strip()]

        # 有可能A选项就不是标准格式
        if nl[0] not in self.option_prefix:
            prefix = nl[0]
            nl = nl[1:]
        else:
            prefix = ""
        # 拆分后长度应该是偶数
        len_nl = len(nl)
        if len_nl % 2 != 0:
            return False, u"拆分后不是偶数"
        # 拆分后应该不超过8
        if len(nl) > 8:
            return False, u"拆分后选项超过4个"

        kp = dict()
        for i in range(0, len_nl, 2):
            if nl[i] not in self.option_prefix:
                return False, u"选项KEY [%s] 不正确 理论上不应该出现的,或者有的选项没有值" % nl[i]
            kp[nl[i]] = nl[i + 1]
        miss_options = []
        # 判断每个选项A B C D是否存在
        for o_index in range(len(self.option_prefix)):
            op = self.option_prefix[o_index]
            if op not in kp.keys():
                # 选项不存在，可能包含在前一个选项里
                p_index = o_index - 1
                if p_index < 0:
                    s_result, pv_values = self.split_special_option(op, prefix)
                    if s_result is False:
                        miss_options.append(op)
                        continue
                        return False, u"有不存在的选项：%s" % op
                    prefix = pv_values[0]
                else:
                    p_p = self.option_prefix[p_index]
                    if p_p not in kp:
                        continue
                    s_result, pv_values = self.split_special_option(op, kp[p_p])
                    if s_result is False:
                        miss_options.append(op)
                        continue
                        # 判断是否有其他选项 如果不包含其他后序选项，说明本身设置选项少
                        return False, u"有不存在的选项：%s" % op
                    kp[p_p] = pv_values[0]
                kp[op] = pv_values[1]
        found = True
        while found and miss_options:
            found = False
            for i in range(len(miss_options) - 1, -1, -1):
                miss_op = miss_options[i]
                _kp = dict()
                for key in kp.keys():
                    s_result, pv_values = self.split_special_option(miss_op,
                                                                    kp[key])
                    if s_result is True:
                        kp[key] = pv_values[0]
                        _kp[miss_op] = pv_values[1]
                        miss_options.remove(miss_op)
                if _kp:
                    found = True
                    kp.update(_kp)
        current_len = len(kp.keys())
        if set(kp.keys()) != set(self.option_prefix[:current_len]):
            # 存在的选项必须是连续的
            for o in self.option_prefix[:current_len]:
                if o not in kp.keys():
                    return False, '有不存在的选项: %s' % o
        options = ListOption(self.option_prefix[:current_len])
        for key in kp.keys():
            setattr(options, key, kp[key])
        return True, {"prefix": prefix, "options": options}

    def parse(self, data):
        if isinstance(data, (list, tuple)):
            s = "\n".join(data)
        else:
            s = data
        s = replace_special_space(s)
        r = self.o_compile.split(s)
        v_result, data = self.verify_split_r(r)
        return v_result, data

    @classmethod
    def test(cls, case_name, s):
        po = cls()
        print(case_name)
        print(po.parse(s))

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
    def test_case3(cls):
        case_name = "测试 选项乱序排列"
        s = u"""A既定资源的配置C资源总量的决定
                B.如何实现充分就业    D.国民收入的决定
            """
        cls.test(case_name, s)

    @classmethod
    def test_case4(cls):
        case_name = "测试 选项题目同一行"
        s = '微观经济学要解决的问题是（A） A.既定资源的配置       B.资源总量的决定 C.如何实现充分就业     D.国民收入的决定'
        cls.test(case_name, s)

    @classmethod
    def test_all(cls):
        cls.test_case1()
        cls.test_case2()
        cls.test_case3()
        cls.test_case4()


if __name__ == "__main__":
    ParseOptions.test_all()

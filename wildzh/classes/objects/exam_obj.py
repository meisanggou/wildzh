# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


class StrategyItemObject(object):
    MAX_NUM = 100

    def __init__(self, **kwargs):
        self._value = None
        self._num = None
        self._qss = []
        self.value = kwargs.pop('value')
        self.num = kwargs.pop('num')
        self.qss = kwargs.pop('qss', [])

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if not isinstance(v, int):
            return
        if v < 0:
            return
        self._value = v

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, v):
        if not isinstance(v, int):
            return
        if v < 0:
            return
        if v > self.MAX_NUM:
            return
        self._num = v

    @property
    def qss(self):
        return self._qss

    @qss.setter
    def qss(self, vs):
        t_min = 0
        t_max = 0
        for v in vs:
            self._qss.append(v)

    def to_dict(self):
        return {'value': self._value, 'num': self._num, 'qss': self._qss}


class StrategyObject(object):
    MAX_LEN = 10

    def __init__(self):
        self.id = None
        self.name = ""
        self.internal = 0
        self._l = []

    def add(self, item):
        if len(self._l) >= self.MAX_LEN:
            return
        if not isinstance(item, StrategyItemObject):
            return
        if item.value is None or item.num is None:
            return
        self._l.append(item)

    def to_dict(self):
        l = [item.to_dict() for item in self._l[:self.MAX_LEN]]
        d = {}
        if self.id:
            d['strategy_id'] = self.id
        if self.name:
            d['strategy_name'] = self.name
        if len(l) > 0:
            d['strategy_items'] = l
        d['internal'] = self.internal
        return d

    def __len__(self):
        return len(self._l)

    @classmethod
    def parse(cls, **kwargs):
        o = cls()
        strategy_name = kwargs.pop('strategy_name', None)
        strategy_id = kwargs.pop('strategy_id', None)
        strategy_items = kwargs.pop('strategy_items', None)
        internal = kwargs.pop('internal', 0)
        if isinstance(strategy_items, list):
            for item in strategy_items:
                item_o = StrategyItemObject(**item)
                o.add(item_o)
            if len(strategy_items) != len(o):
                return None
            if len(o) <= 0:
                return None
        o.id = strategy_id
        o.name = strategy_name
        o.internal = internal
        return o

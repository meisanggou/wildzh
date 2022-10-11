# !/usr/bin/env python
# coding: utf-8
from wildzh.utils import constants


__author__ = 'zhouhenglc'


class ExamOpennessLevel(object):
    PRIVATE = 'private'
    SEMI_PUBLIC = 'semi-public'
    PUBLIC = 'public'


class ExamOpenMode(object):
    NONE = 0
    SUBJECT = 1
    ANSWER = 2
    ANALYSIS = 4
    SUBJECT_ANSWER = 3
    ALL = 7


class AttrEnableVideo(object):

    def __init__(self):
        self._enable_video = 0

    @property
    def enable_video(self):
        return self._enable_video

    @enable_video.setter
    def enable_video(self, v):
        if v:
            self._enable_video = 1
        else:
            self._enable_video = 0


class ExamObject(AttrEnableVideo):
    extend_keys = ['openness_level', 'open_mode', 'open_no_start',
                   'open_no_end', 'pic_url', 'subjects', 'allow_search',
                   'search_tip', 'select_modes', 'enable_video']

    def __init__(self, **kwargs):
        super().__init__()
        self._d = dict()
        self.exam_no = None
        self.exam_name = None
        self.exam_desc = None
        self.adder = None
        self.status = None
        self.exam_num = None
        self.question_num = None
        self._openness_level = ExamOpennessLevel.PRIVATE
        self._open_mode = ExamOpenMode.SUBJECT
        self._open_no_start = -1
        self._open_no_end = None
        self._allow_search = 0
        self._search_tip = ""
        self._select_modes = []
        self._subjects = []

        self.pic_url = None
        self._exam_role = 100
        self.update(**kwargs)

    def update(self, **kwargs):
        exam_extend = kwargs.pop('exam_extend', dict())
        for k, v in kwargs.items():
            if hasattr(self, k):
                self._internal_set(k, v)
        if isinstance(exam_extend, dict):
            for k in self.extend_keys:
                if k in exam_extend:
                    self._internal_set(k, exam_extend[k])
                elif hasattr(self, '_%s' % k):
                    self._internal_set(k, getattr(self, '_%s' % k))

    @property
    def openness_level(self):
        if not hasattr(self, '_openness_level'):
            self._openness_level = ExamOpennessLevel.PRIVATE
        return self._openness_level

    @openness_level.setter
    def openness_level(self, v):
        v = v.lower()
        if v == ExamOpennessLevel.PUBLIC:
            self._exam_role = 10
            self._open_mode = ExamOpenMode.ALL

        elif v == ExamOpennessLevel.SEMI_PUBLIC:
            self._exam_role = 25
        else:
            v = ExamOpennessLevel.PRIVATE
            self._exam_role = 100
            self._open_mode = ExamOpenMode.NONE
        self._openness_level = v
        self._d['openness_level'] = v
        self.open_mode = self._open_mode

    def is_private(self):
        return self.openness_level == ExamOpennessLevel.PRIVATE

    @property
    def open_mode(self):
        if not hasattr(self, '_open_mode'):
            self._open_mode = ExamOpenMode.SUBJECT
        return self._open_mode

    @open_mode.setter
    def open_mode(self, v):
        if isinstance(v, (str, )):
            v = ExamOpenMode.SUBJECT
        if self._openness_level == ExamOpennessLevel.SEMI_PUBLIC:
            if v == ExamOpenMode.ALL:
                self._exam_role = 20
            elif v == ExamOpenMode.SUBJECT_ANSWER:
                self._exam_role = 22
            else:
                v = ExamOpenMode.SUBJECT
                self._exam_role = 25
        self._open_mode = v
        self._d['open_mode'] = v

    @property
    def open_no_start(self):
        return self._open_no_start

    @open_no_start.setter
    def open_no_start(self, v):
        if isinstance(v, (str, )):
            v = v.strip()
        if v == '' or v is None:
            v = -1
            cv = ''
        else:
            v = int(v)
            cv = v
        self._open_no_start = v
        self._d['open_no_start'] = cv

    @property
    def open_no_end(self):
        return self._open_no_end

    @open_no_end.setter
    def open_no_end(self, v):
        if isinstance(v, (str, )):
            v = v.strip()
        if v == '' or v is None:
            v = None
            cv = ''
        else:
            v = int(v)
            cv = v
        self._open_no_end = v
        self._d['open_no_end'] = cv

    @property
    def allow_search(self):
        return self._allow_search

    @allow_search.setter
    def allow_search(self, v):
        if v in (1, '1'):
            self._allow_search = 1
        else:
            self._allow_search = 0
        self._d['allow_search'] = self._allow_search

    @property
    def search_tip(self):
        return self._search_tip

    @search_tip.setter
    def search_tip(self, v):
        if v is None:
            v = ''
        self._search_tip = v.strip()
        self._d['search_tip'] = self._search_tip

    @property
    def exam_role(self):
        if not hasattr(self, '_exam_role'):
            self._exam_role = 100
        return self._exam_role

    def verify_no(self, no):
        if self.open_mode == ExamOpennessLevel.PRIVATE:
            return False
        if self.open_mode == ExamOpennessLevel.PUBLIC:
            return True
        if self.open_no_end is None:
            _end = float('INF')
        else:
            _end = self.open_no_end
        if self.open_no_start <= no <= _end:
            return True
        return False

    def _can_access(self, t_v):
        return (self._open_mode & t_v) == t_v

    def can_look_analysis(self):
        return self._can_access(ExamOpenMode.ANALYSIS)

    def can_look_answer(self):
        return self._can_access(ExamOpenMode.ANSWER)

    def can_look_subject(self):
        return self._can_access(ExamOpenMode.SUBJECT)

    @property
    def select_modes(self):
        return self._select_modes

    @select_modes.setter
    def select_modes(self, values):
        if not isinstance(values, list):
            return
        if len(values) < len(self._select_modes):
            return
        index = 0
        for item in values:
            if 'enable' not in item:
                return
            if 'name' not in item:
                item['name'] = constants.G_SELECT_MODE[index]
            if 'multi' not in item:
                if index in constants.G_MULTI_MODE:
                    item['multi'] = True
                else:
                    item['multi'] = False
            index += 1
        if len(values) != len(constants.G_SELECT_MODE):
            index = 0
            for item in values:
                if item['name'] != constants.G_SELECT_MODE[index]:
                    # TODO write warning
                    break
                index += 1
            else:
                for i in range(index, len(constants.G_SELECT_MODE)):
                    values.append({'name': constants.G_SELECT_MODE[i],
                                   'enable': False})
        self._select_modes = values

    @property
    def subjects(self):
        return self._subjects

    @subjects.setter
    def subjects(self, values):
        if not isinstance(values, list):
            return
        if len(values) < len(self._subjects):
            return
        index = 0
        while index < len(values):
            n_sj = values[index]
            if 'name' not in n_sj:
                return
            if len(n_sj['name']) <= 0:
                return
            # n_sms = n_sj['select_modes']
            o_sms_l = 0
            # if index < len(self._subjects):
                # o_sms_l = len(self._subjects[index]['select_modes'])
            # if len(n_sms) < o_sms_l:
            #     return
            # for sm in n_sms:
            #     if 'name' not in sm or 'enable' not in sm:
            #         return
            chapters = []
            for cp in n_sj['chapters']:
                if isinstance(cp, (str, )):
                    cp_item = {'name': cp, 'enable': True}
                elif cp['enable'] is False:
                    continue
                else:
                    cp_item = cp
                chapters.append(cp_item)
            n_sj['chapters'] = chapters
            index += 1
        self._subjects = values
        self._d['subjects'] = self._subjects

    def _internal_set(self, k, v):
        self._d[k] = v
        setattr(self, k, v)

    def to_dict(self):
        return self._d

    def to_db_dict(self):
        _d = {'exam_name': self.exam_name, 'exam_desc': self.exam_desc}
        if self.exam_no:
            _d['exam_no'] = self.exam_no
        else:
            _d['adder'] = self.adder
        for key in self.extend_keys:
            _d[key] = getattr(self, key)
        return _d


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

# !/usr/bin/env python
# coding: utf-8
from wildzh.classes import DBObject

__author__ = 'zhouhenglc'


class MPVersion(DBObject):
    table = 'version_mp'
    columns = ['user_no', 'version', 'max_version', 'min_version',
               'last_modify']

    @classmethod
    def cmp_version(cls, version1, version2):
        vs1 = list(map(lambda x: int(x), version1.split('.')))
        vs2 = list(map(lambda x: int(x), version2.split('.')))
        for v1, v2 in zip(vs1, vs2):
            if v1 > v2:
                return 1
            if v2 > v1:
                return -1
        if len(vs1) > len(vs2):
            return 1
        if len(vs2) > len(vs1):
            return -1
        return 0

    def insert(self, user_no, version):
        data = dict(user_no=user_no, version=version,
                    max_version=version, min_version=version,
                    last_modify=self.now_time)
        l = self.db.execute_insert(self.t, kwargs=data)
        return l

    def select(self, user_no):
        where_value = dict(user_no=user_no)
        items = self.db.execute_select(self.t, where_value=where_value,
                                       cols=self.cols)
        if len(items) > 0:
            return items[0]
        return None

    def _update(self, user_no, **kwargs):
        where_value = dict(user_no=user_no)
        kwargs['last_modify'] = self.now_time
        l = self.db.execute_update(self.t, where_value=where_value,
                                   update_value=kwargs)
        kwargs.update(where_value)
        return kwargs

    def update_version(self, user_no, version):
        item = self.select(user_no=user_no)
        if item:
            version_obj = item
            version_obj['version'] = version
            if self.cmp_version(version, version_obj['max_version']) > 0:
                version_obj['max_version'] = version
            if self.cmp_version(version_obj['min_version'], version) > 0:
                version_obj['min_version'] = version
            return self._update(**version_obj)
        return self.insert(user_no, version)

# !/usr/bin/env python
# coding: utf-8
from wildzh.classes import BaseObject

from wildzh.db.models.version import VersionMPModel

__author__ = 'zhouhenglc'


class VersionMP(BaseObject):
    model = VersionMPModel

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

    def update_version(self, session, user_no, version):
        items = self.get_all(session, user_no=user_no)
        if items:
            version_obj = items[0]
            if version_obj.version == version:
                return version_obj
            version_obj.version = version
            if self.cmp_version(version, version_obj.max_version) > 0:
                version_obj.max_version = version
            if self.cmp_version(version_obj.min_version, version) > 0:
                version_obj.min_version = version
            version_obj.last_modify = self.now_time
            return version_obj
        kwargs = {'version': version, 'min_version': version,
                  'max_version': version, 'last_modify': self.now_time}
        return self.create(session, user_no=user_no, **kwargs)

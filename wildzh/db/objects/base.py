#! /usr/bin/env python
# coding: utf-8

import time
import uuid


class BaseObject(object):
    model = None
    uuid_col = None

    @property
    def now_time(self):
        return time.time()

    def query(self, session, **kwargs):
        query = session.query(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query

    def create(self, session, **kwargs):
        if hasattr(self.model, 'update_time'):
            kwargs['update_time'] = self.now_time
        if hasattr(self.model, 'add_time'):
            kwargs['add_time'] = self.now_time
        if self.uuid_col:
            kwargs[self.uuid_col] = str(uuid.uuid4())
        obj = self.model(**kwargs)
        obj.save(session)
        return obj

    def get_all(self, session, **kwargs):
        return session.query(self.model).filter_by(**kwargs).all()

    def update(self, session, where_value, **kwargs):
        if hasattr(self.model, 'update_time'):
            kwargs['update_time'] = self.now_time
        return session.query(self.model).filter_by(**where_value).update(
            kwargs)

    def delete(self, session, **kwargs):
        return session.query(self.model).filter_by(**kwargs).delete()

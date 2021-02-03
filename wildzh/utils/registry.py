# !/usr/bin/env python
# coding: utf-8

import collections
import inspect


class CallbacksManager(object):
    _instance = None

    def __init__(self):
        if not hasattr(self, 'callbacks'):
            self.callbacks = collections.defaultdict(dict)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def subscribe(self, callback, resource, event):
        callback_list = self.callbacks[resource].setdefault(event, [])
        callback_list.append(callback)

    def notify(self, resource, event, trigger, **kwargs):
        callbacks = self.callbacks[resource].get(event, [])
        for callback in callbacks:
            callback(resource, event, trigger, **kwargs)

    def clear(self):
        self.callbacks = collections.defaultdict(dict)


_CALLBACK_MANAGER = None

# stores a dictionary keyed on function pointers with a list of
# (resource, event) tuples to subscribe to on class initialization
_REGISTERED_CLASS_METHODS = collections.defaultdict(list)


def _get_callback_manager():
    global _CALLBACK_MANAGER
    if _CALLBACK_MANAGER is None:
        _CALLBACK_MANAGER = CallbacksManager()
    return _CALLBACK_MANAGER


def notify(resource, event, trigger, **kwargs):
    _get_callback_manager().notify(resource, event, trigger, **kwargs)


def subscribe(callback, resource, event):
    _get_callback_manager().subscribe(callback, resource, event)


def clear():
    _get_callback_manager().clear()

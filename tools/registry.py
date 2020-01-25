# !/usr/bin/env python
# coding: utf-8

import collections
import inspect


class CallbacksManager(object):
    _instance = None

    def __init__(self):
        self.callbacks = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def notify(self, resource, event, trigger, **kwargs):
        pass

    def clear(self):
        pass


_CALLBACK_MANAGER = None

# stores a dictionary keyed on function pointers with a list of
# (resource, event) tuples to subscribe to on class initialization
_REGISTERED_CLASS_METHODS = collections.defaultdict(list)


def _get_callback_manager():
    global _CALLBACK_MANAGER
    if _CALLBACK_MANAGER is None:
        _CALLBACK_MANAGER = CallbacksManager()
    return _CALLBACK_MANAGER


# NOTE(boden): This method is deprecated in favor of publish() and will be
# removed in Queens, but not deprecation message to reduce log flooding
def notify(resource, event, trigger, **kwargs):
    _get_callback_manager().notify(resource, event, trigger, **kwargs)


def clear():
    _get_callback_manager().clear()

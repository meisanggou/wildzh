# !/usr/bin/env python
# coding: utf-8

import collections
import inspect

from flask_helper.exception import RepeatCallback

# TODO use flask_helper.utils.registry

class HookRegistry(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_dict'):
            self._dict = collections.defaultdict(dict)
            self._one_dict = collections.defaultdict(dict)

    @staticmethod
    def _get_id(callback):
        # TODO
        return callback.__name__

    @classmethod
    def get_instance(cls):
        if cls._instance is not None:
            return cls._instance
        return cls()

    def subscribe(self, callback, resource, event):
        callback_list = self._dict[resource].setdefault(event, [])
        callback_id = self._get_id(callback)
        for ck in callback_list:
            if callback_id == self._get_id(ck):
                return
        callback_list.append(callback)

    def notify(self, resource, event, trigger, **kwargs):
        callbacks = self._dict[resource].get(event, [])
        for callback in callbacks:
            callback(resource, event, trigger, **kwargs)

    def set_callback(self, callback, resource, event):
        if event in self._one_dict[resource]:
            raise RepeatCallback(resource, event)
        self._one_dict[resource][event] = callback

    def callback(self, resource, event, trigger, **kwargs):
        callback_fun = self._one_dict[resource].get(event, None)
        if callback_fun:
            return callback_fun(resource, event, trigger, **kwargs)


_CALLBACK_MANAGER = None


def _get_callback_manager():
    global _CALLBACK_MANAGER
    if _CALLBACK_MANAGER is None:
        _CALLBACK_MANAGER = HookRegistry()
    return _CALLBACK_MANAGER


def notify(resource, event, trigger, **kwargs):
    _get_callback_manager().notify(resource, event, trigger, **kwargs)


def subscribe(callback, resource, event):
    _get_callback_manager().subscribe(callback, resource, event)


def clear():
    _get_callback_manager().clear()


_REGISTERED_CLASS_METHODS = collections.defaultdict(list)
_REGISTERED_CLASS_CALLBACK = collections.defaultdict(list)

_HOOK = _get_callback_manager()


def subscribe_callback(*args):
    if len(args) == 2:
        resource = args[0]
        event = args[1]
    elif len(args) == 3:
        callback = args[0]
        resource = args[1]
        event = args[2]
        return _subscribe_callback(callback, resource, event)
    else:
        raise RuntimeError('require args: callback, resource, event')
    def decorator(f):
        subscribe_callback(f, resource, event)
        return f
    return decorator


def _subscribe_callback(callback, resource, event):
    return _HOOK.set_callback(callback, resource, event)


def notify_callback(resource, event,trigger, **kwargs):
    return _HOOK.callback(resource, event, trigger, **kwargs)


def receives(resource, events):
    def decorator(f):
        for e in events:
            _REGISTERED_CLASS_METHODS[f].append((resource, e))
        return f
    return decorator


def receive_callback(resource, event):
    def decorator(f):
        _REGISTERED_CLASS_CALLBACK[f].append((resource, event))
        return f
    return decorator


def has_registry_receivers(old_cls):
    orig_new = old_cls.__new__
    new_inherited = '__new__' not in old_cls.__dict__

    @staticmethod
    def replacement_new(cls, *args, **kwargs):
        if new_inherited:
            super_new = super(old_cls, cls).__new__
            if super_new is object.__new__:
                instance = super_new(cls)
            else:
                instance = super_new(cls, *args, **kwargs)
        else:
            instance = orig_new(cls, *args, **kwargs)
        _k = '_DECORATED_METHODS_SUBSCRIBED'
        if getattr(instance, _k, False):
            return instance
        for name, unbound_method in inspect.getmembers(cls):
            if (not inspect.ismethod(unbound_method) and
                    not inspect.isfunction(unbound_method)):
                continue
            func = getattr(unbound_method, 'im_func', unbound_method)
            if func in _REGISTERED_CLASS_METHODS:
                for resource, event in _REGISTERED_CLASS_METHODS[func]:
                    _HOOK.subscribe(getattr(instance, name), resource, event)
            elif func in _REGISTERED_CLASS_CALLBACK:
                for resource, event in _REGISTERED_CLASS_CALLBACK[func]:
                    _HOOK.set_callback(getattr(instance, name), resource, event)
        setattr(instance, _k, True)
        return instance
    old_cls.__new__ = replacement_new
    return old_cls

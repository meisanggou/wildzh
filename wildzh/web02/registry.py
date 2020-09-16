# !/usr/bin/env python
# coding: utf-8
import collections
import inspect

from flask_helper.utils.registry import HookRegistry

__author__ = 'zhouhenglc'

_REGISTERED_CLASS_METHODS = collections.defaultdict(list)
_REGISTERED_CLASS_CALLBACK = collections.defaultdict(list)

_HOOK = HookRegistry()


def notify(resource, event, trigger, **kwargs):
    _HOOK.notify(resource, event, trigger, **kwargs)


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

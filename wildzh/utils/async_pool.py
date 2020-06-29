# !/usr/bin/env python
# coding: utf-8
from functools import partial
import threading
from threading import Thread
import uuid

__author__ = 'zhouhenglc'


class Task(object):
    maps = {}

    def __init__(self, task_id=None):
        if task_id is None:
            task_id = uuid.uuid4().hex
        self.task_id = task_id
        self.maps[self.task_id] = self
        self.thread_item = None
        self.is_complete = False

    @property
    def complete(self):
        return self.is_complete

    def set_complete(self):
        self.is_complete = True

    def __str__(self):
        s = '%s<%s>' % (self.task_id, self.is_complete)
        return s


class AsyncWorker(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, max_workers=1):
        if not hasattr(self, '_executor'):
            self._executor = None
        self.max_workers = getattr(self, 'max_workers', max_workers)
        self.current_tasks = getattr(self, 'current_tasks', [])
        self.wait_queue = getattr(self, 'wait_queue', [])
        self.t_lock = getattr(self, 't_lock', threading.Lock())

    def resize(self, max_workers):
        self.max_workers = max_workers
        self.try_start_thread()

    def try_start_thread(self):
        if len(self.wait_queue) <= 0:
            return
        self.t_lock.acquire()
        run_count = 0
        for i in range(len(self.current_tasks) - 1, -1, -1):
            ct = self.current_tasks[i]
            if not ct.complete:
                run_count += 1
            else:
                self.current_tasks.pop(i)
        while run_count < self.max_workers:
            if len(self.wait_queue) <= 0:
                break
            _func, args, kwargs = self.wait_queue.pop(0)
            task = Task()
            n_func = partial(self._proxy_function, _func, task)
            t = Thread(target=n_func, args=args, kwargs=kwargs)
            task.thread_item = t
            self.current_tasks.append(task)
            t.start()
            run_count += 1
        self.t_lock.release()

    def _proxy_function(self, func, task_item, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(e)
        except SystemExit as se:
            print(se)
        task_item.set_complete()
        self.try_start_thread()

    def submit(self, fn, *args, **kwargs):
        self.wait_queue.append((fn, args, kwargs))
        self.try_start_thread()

    def submit_task(self, task_id, interval, fn, *args, **kwargs):
        return self.submit(fn, *args, **kwargs)

    def __call__(self, fn, *args, **kwargs):
        return self.submit(fn, *args, **kwargs)


_POOL = None


def get_pool():
    global _POOL
    if _POOL is None:
        _POOL = AsyncWorker(5)
    return _POOL


if __name__ == '__main__':
    import time
    aw = AsyncWorker(3)
    def func(s):
        print(s)
        time.sleep(5)
        print('%s end' % s)
    aw.submit(func, 'hello world')
    aw.submit(func, 'hello world')
    aw = AsyncWorker(3)
    aw.submit(func, 'hello world')

    aw = AsyncWorker(4)
    aw.submit(func, 'hello world')
    aw.submit(func, 'hello world')
    time.sleep(1)
    aw.resize(5)
    aw.submit(func, 'hello world')
    time.sleep(100)

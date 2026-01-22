"""
Modify from:
    http://www.s1nh.org/post/python-different-ways-to-kill-a-thread/
"""
import ctypes
import threading
from typing import List

from loguru import logger

PyGILState_Ensure = ctypes.pythonapi.PyGILState_Ensure
PyGILState_Release = ctypes.pythonapi.PyGILState_Release

""" 自定义异常：终止线程时抛这个异常 """
class ThreadKilledError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)

""" 自定义异常：终止失败时抛这个异常 """
class ThreadCanNotBeKilledError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)

""" 继承原生Thread，扩展“可杀死”能力 """
class KillableThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self._killed = False    # 标记线程是否已被杀死
        add_thread(self)        # 注册到全局列表

    # 获取线程ID（Python线程没有直接的id属性，需从活跃线程表查）
    def get_id(self):
        """
        Get the id of the respective thread.
        Returns: Thread id.

        """
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    # 核心：强制杀死线程（不安全！类比Java废弃的Thread.stop()）
    def kill(self):
        """
        Kill the thread unsafely.
        Notes: This is an unsafe method the thread execution may be corrupted.
        Throws: ThreadCanNotBeKilledError if the thread is not killed successfully.
                ThreadKilledError if the thread is killed successfully.

        """
        thread_id = self.get_id()
        # 调用Python底层C API：给指定线程抛ThreadKilledError异常
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(ThreadKilledError))
        if res > 1: # 抛异常失败，需要清理
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            raise ThreadCanNotBeKilledError('Exception raise failure')
        self._killed = True

    # 持有GIL时杀死线程（Python的GIL是全局解释器锁，多线程必懂）
    def kill_with_gil_held(self):
        gstate = PyGILState_Ensure()
        try:
            self.kill()
        finally:
            PyGILState_Release(gstate)

    # 重写join：如果线程已被杀死，直接返回（不用等）
    def join(self, timeout=None):
        """
        Notes: If the thread is killed successfully will not join.
        Args:
            timeout:

        Returns:

        """
        if self._killed:
            return
        else:
            super().join(timeout)

# 全局存储所有KillableThread实例
_all: List[KillableThread] = []

""" 注册线程 """
def add_thread(t: KillableThread):
    assert isinstance(t, KillableThread)
    _all.append(t)

""" 批量杀死所有注册的线程 """
def kill_all_threads():
    for thread in _all:
        try:
            thread.kill()
            logger.debug(f"Thread {thread.get_id()}: killed")
        except ThreadCanNotBeKilledError:
            logger.error(f"Failed to kill thread: {thread.get_id()}")
    logger.debug("All threads killed.")

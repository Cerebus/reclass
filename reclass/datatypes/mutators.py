#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–14 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#

from collections import deque

class Mutators(object):
    '''
    A class to maintain a push-only stack of python callables, with the following specialty:

        + If a callable is being pushed onto the stack which is already there,
          it is removed from its previous position and placed back on top

    Class also provides a static method for building lists of callables from iterables
    of module paths
    '''
    @staticmethod
    def load_callables(iterable):
        callables = []
        for path in iterable:
            modname, callname = path.rsplit('.', 1)
            module  = __import__(modname, globals(), locals(), [callname], -1)
            call    = getattr(module, callname)
            callables.append(call)
        return callables
    def __init__(self, iterable=None):
        self._stack = deque()
        if iterable is not None:
            self.push(iterable)
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__,
                           self.as_list())
    def __len__(self):
        return len(self._stack)
    def __eq__(self, rhs):
        if isinstance(rhs, deque):
            return self._stack == rhs
        if isinstance(rhs, list):
            return list(self._stack) == rhs
        else:
            try:
                return self._stack == rhs._stack
            except AttributeError:
                return False
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
    def push(self, iterable):
        if isinstance(iterable, self.__class__):
            iterable = iterable.as_list()
        for item in iterable:
            if item in self._stack:
                self._stack.remove(item)
            self._stack.appendleft(item)
    def as_list(self):
        return list(self._stack)
    def as_deque(self):
        return deque(self._stack)
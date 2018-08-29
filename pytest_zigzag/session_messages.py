# -*- coding: utf-8 -*-


class SessionMessages(object):
    """A class to contain a list of messages"""
    def __init__(self):
        self._lst = []

    def __getitem__(self, item):
        return self._lst[item]

    def __getattr__(self, method):
        return getattr(self._lst, method)

    def drain(self):
        """Empties the list of all its values"""
        self._lst = []

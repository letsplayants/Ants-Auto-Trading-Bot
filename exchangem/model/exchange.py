# -*- coding: utf-8 -*-

"""
거래소가 반드시 가져야하는 기능 목록을 넣어둔다.
"""

import abc
from model.observers import ObserverNotifier

class Base(ObserverNotifier, metaclass=abc.ABCMeta):
    def __init__(self):
        ObserverNotifier.__init__(self)
        
    pass
    # @abc.abstractmethod
    # def func1(self):
    #     pass



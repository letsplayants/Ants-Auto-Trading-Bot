# -*- coding: utf-8 -*-

import abc
import logging
import ccxt

class StrategyBase(metaclass=abc.ABCMeta):
    def __init__(self, args={}):
        pass
    
    @abc.abstractmethod
    def run(self):
        pass
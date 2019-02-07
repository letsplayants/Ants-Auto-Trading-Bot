# -*- coding: utf-8 -*-

"""
거래소가 반드시 가져야하는 기능 목록을 넣어둔다.
"""

import abc
from exchangem.model.observers import ObserverNotifier
from exchangem.utils import Util

class Base(ObserverNotifier, metaclass=abc.ABCMeta):
    def __init__(self):
        ObserverNotifier.__init__(self)
        orderes = []
    pass
    
    def loadKey(self, file_name):
        return Util.readKey(file_name)
        
    @abc.abstractmethod
    def get_balance(self, target):
        pass
    
    @abc.abstractmethod
    def _order(self, args):
        """
        각 거래소마다 지정된 형태로 오더를 내린다
        
        args['market'] = market
        args['coin_name'] = coin_name
        args['action'] = action #BUY or SELL
        args['price'] = price
        args['count'] = count
        """
        pass
    
    def order(self, market, coin_name, action, price, count):
        args = []
        args['market'] = market
        args['coin_name'] = coin_name
        args['action'] = action #BUY or SELL
        args['price'] = price
        args['count'] = count
        
        try:
            order_id = self._order(args)
            self.orders.append(order_id)
        except Exception as e:
            logger.warning(e)
    
    

class SupportWebSocket(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def open(self):
        pass
    
    @abc.abstractmethod
    def close(self):
        pass
    
    @abc.abstractmethod
    def connect(self):
        pass
    

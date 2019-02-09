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
        self.exchange = None
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
    
    @abc.abstractmethod
    def check_amount(self, coin_name, seed_size, price):
        """
        코인 이름과 시드 크기를 입력받아서 매매 가능한 값을 돌려준다
        이때 수수료 계산도 함께 해준다
        매매가능한 크기가 거래소에서 지정한 조건에 부합하는지도 함께 계산해서
        돌려준다
        
        가령 주문 단위가 10으로 나눠서 떨어져야 한다면 계산값이 11이 나올경우
        10으로 돌려준다
        주문 가격이 오류인 경우 price오류와 함께 예외를 발생시킨다
        
        return 매매가능한 양, 가격, 수수료
        """
        pass

    @abc.abstractmethod
    def get_last_price(self, coin_name):
        pass

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
    

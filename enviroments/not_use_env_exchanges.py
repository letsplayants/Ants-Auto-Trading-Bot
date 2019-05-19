# -*- coding: utf-8 -*-
import logging
import consts
import json
import sys

from messenger.q_publisher import MQPublisher
from exchangem.model.coin_model import CoinModel

class ExchangesEnv(BaseClass, metaclass=Singleton):
    """
    거래소 관련 환경 값을 가지고 있는다
    Enviroments의 exchanges를 레퍼런스 참조하는 방식으로 설계 및 구현한다
    exchanges에 관련된 값을 조회/조작하는 기능을 제공한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.exchanges = Enviroments().exchanges
        
    def __repr__(self):
        return str(dict(self))
    
    def set_default(self):
        Enviroments().exchanges = {}
        self.exchanges = Enviroments().exchanges
        self.exchanges['default'] = self.get_default_setting()
    
    def get_default_setting(self):
        coin = CoinModel()
        coin.amount.available = 1000
        coin.amount.keep = 0
        
        coins = {
            'default' : dict(coin)
        }
        
        keys = {
            'apiKey':'',
            'secret':''
        }
        
        trading_list = {
            'all' : True,
            'list' : []
        }
        
        default_setting = {
            'coin' : coins,
            'keys' : keys,
            'traing_list' : trading_list
        }
        
        return default_setting
    
    def getExchange(self, name):
        if(self.exhcnages.get(name) is None):
            self.exhcnages[name] = self.default_setting()
        return self.exchanges[name]
    
    def get_trading_list(self, name):
        if(self.exchanges.get(name).get('trading_list') is None):
            self.exchanges[name]['trading_list'] = {'all' : True, 'list' : []}
        return self.exchanges[name]['trading_list']
    
    
if __name__ == '__main__':
    print('Exchanges Enviroments test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    import os
    path = os.path.dirname(__file__) + '/../configs/ant_auto.conf'
    Enviroments().load_config(path)
    
    # print(consts.ENV)
    # print(en1)
    # print(en1.common)
    # print(en2.common)

    # dt = vars(en1)
    # print(dt)

    # j = en1.to_json()
    # print(j)
    
    # en1.from_json(j)
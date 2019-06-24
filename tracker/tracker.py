# -*- coding: utf-8 -*-
import logging

from price_tracker import PriceTracker
from messenger.q_publisher import MQPublisher
from env_server import Enviroments

class BaseClass():
	pass

class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class Tracker(BaseClass, metaclass=Singleton):
    """
    요청이 들어오면 추적기를 달아준다.
    제공하는 추적기는 오더 추적기와 가격 추적기이다.
    요청은 모두 큐를 사용해서 받는다.
    RPC 방식으로 호출될 함수를 넣어서 전달한다.
    
    요청할 때 조건을 만족할 때 호출된 함수를 넣어서 큐에 넣는다.
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        
        self.telegram_messenger_exchange_name = Enviroments().qsystem.get_telegram_messenge_q()
        self.messenger_q = MQPublisher(self.telegram_messenger_exchange_name)
        self.logger.debug(f'telegram message q name : {self.telegram_messenger_exchange_name}')
        self.exchanges = {}
        self.price_tracker = PriceTracker()
        
    def add_exchange(self, name, exchange):
        self.exchanges[name.upper()] = exchange
        
    def get_exchange(self, name):
        return self.exchanges[name.upper()]
    
    
    
if __name__ == '__main__':
    print('strategy test')
    
    import os
    path = os.path.dirname(__file__) + '/../configs/ant_auto.conf'
    print('path : {}'.format(path))
    Enviroments().load_config(path)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("exchangem").setLevel(logging.ERROR)
    logging.getLogger("exchange").setLevel(logging.ERROR)
    
 
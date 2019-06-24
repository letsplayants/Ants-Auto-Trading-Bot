# -*- coding: utf-8 -*-
import logging
import threading
import time

from price_model import PriceModel

from exchangem.model.price_storage import PriceStorage
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

class PriceTracker(BaseClass, metaclass=Singleton):
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.loop = True
        self.interval = 3
        self.monitoring_list = []
        self.run()
    
    def __run__(self):
        ps = PriceStorage()
        while self.loop:
            time.sleep(self.interval)
            #TODO 아래 루프를 수행 시간을 측정해서 interval을 조정해야한다
            for item in self.monitoring_list:
                exchange = item['exchange']
                coin = item['coin']
                market = item['market']
                tp = float(item['target_price'])
                hl = item['high_eq_low']
                cb = item['callback']
                
                now_price = float(ps.get_price(exchange, market, coin)['price'])
                
                self.logger.debug(f'{coin}\t{tp}\tnow:{now_price}')
                
                if(hl.upper() == 'HIGH'):
                    if(tp <= now_price):
                        cb(item)
                        self.monitoring_list.remove(item)
                elif(hl.upper() == 'LOW'):
                    if(tp >= now_price):
                        cb(item)
                        self.monitoring_list.remove(item)
                
    def run(self):
        self.thread_hnd = threading.Thread(target=self.__run__, args=())
        self.thread_hnd.start()
    
    def add_event(self, item):
        """
        item['exchange']
        item['coin']
        item['market']
        item['target_price']
        item['high_eq_low'] 타겟가 이상 또는 이하
        item['callback'] 콜백함수
        """
        self.monitoring_list.append(item)
    
    
        
if __name__ == '__main__':
    print('price_tracker test')
    
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
    logging.getLogger("websockets").setLevel(logging.WARNING)
    
    #TODO TSB에서 입력된 가격보다 1%이상 차이나면 매수/매도를 취소하거나 재조정한다
    
    from exchangem.exchanges.upbit import Upbit
    
    upbit = Upbit()
    pt = PriceTracker()
    
    def callback(item):
        print('-'*120)
        print('-'*120)
        print('event trigger with {}'.format(item))
        print('-'*120)
        print('-'*120)
        
        # item = {}
        # item['exchange'] = 'UPBIT'
        # item['coin'] = 'BTC'
        # item['market'] = 'KRW'
        # item['target_price'] = '10000000'
        # item['high_eq_low'] = 'HIGH'
        # item['callback'] = callback
        
        # pt.add_event(item)
    
    item = PriceModel()
    
    item['exchange'] = 'UPBIT'
    item['coin'] = 'BTC'
    item['market'] = 'KRW'
    item['target_price'] = '10000000'
    item['high_eq_low'] = 'HIGH'
    item['callback'] = callback
    item['raw'] = {
        'from' : 'tsb-34-10m'
    }
    
    
    
    while True:
        pt.add_event(item)
        time.sleep(60)
# -*- coding: utf-8 -*-
import logging
import threading
import time

from exchangem.exchanges.upbit import Upbit
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

class OrderTracker(BaseClass, metaclass=Singleton):
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.loop = True
        self.interval = 10
        self.upbit = Upbit({'no_async':True})
        self.open_order_list = {}   #체결량 0
        self.done_order_list = {}   #체결 완료
        self.cancel_order_list = {} #주문 취소(체결 도중 취소는 체결 완료로 처리)
        self.run()
    
    def __order_check__(self):
        states = ['done', 'cancel', 'wait']
        # for s in states:
        #     self.upbit.get_private_orders_by_state(s)
        
        # order_id = item['id']
        # exchange = item['exchange']
        # coin = item['coin']
        # market = item['market']
        # tp = float(item['target_price'])
        # hl = item['high_eq_low']
        # cb = item['callback']
        
        # now_price = float(ps.get_price(exchange, market, coin)['price'])
        
        # self.logger.debug(f'{coin}\t{tp}\tnow:{now_price}')
        
        # if(hl.upper() == 'HIGH'):
        #     if(tp <= now_price):
        #         cb(item)
        #         self.order_list.remove(item)
        # elif(hl.upper() == 'LOW'):
        #     if(tp >= now_price):
        #         cb(item)
        #         self.order_list.remove(item)
    
    def __get_all_order_list__(self):
        order_list = []
        for i in self.open_order_list:
            order_list.append(i)
            
        if(len(order_list) <= 0):
            return
        
        updated_list = self.upbit.get_trading_list(order_list)
        print(updated_list)
        for item in updated_list:
            if(item['state'] == 'wait'):
                continue
            
            order = self.open_order_list[item['uuid']]
            del self.open_order_list[item['uuid']]
            if(item['state'] == 'cancel'):
                self.cancel_order_list[item['uuid']] = item
            elif (item['state'] == 'done'):
                self.done_order_list[item['uuid']] = item
                
            order['etc']['callback'](item)
            
    
    def __run__(self):
        ps = PriceStorage()
        while self.loop:
            all_order_list = self.__get_all_order_list__()
            self.logger.debug(all_order_list)
            
            time.sleep(self.interval)
        
    def run(self):
        self.thread_hnd = threading.Thread(target=self.__run__, args=())
        self.thread_hnd.start()
    
    def add_order(self, item):
        """
        {'symbol': 'BTC/KRW', 'id': '1b27dd06-9cb5-4c46-bf20-f1f91a60b6fb', 'side': 'buy', 'price': 100000.0, 'amount': 1.0, 'status': 'open', 'remaining': 1.0, 'ts_create': 1560996340000, 'ts_updated': None}
        item['exchange']
        item['callback'] #콜백함수
        item['tp'] = [event1, event2, ...]
        item['sp'] = [event1, event2, ...]
        item['raw'] = {
            'sub_orderes' : [1,2,3,4]
        }
        """
        self.open_order_list[item['id']] = item
    
    
        
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
    # logging.getLogger("exchangem").setLevel(logging.WARNING)
    # logging.getLogger("exchange").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)
    
    #TODO TSB에서 입력된 가격보다 1%이상 차이나면 매수/매도를 취소하거나 재조정한다
    
    ot = OrderTracker()
    
    def callback(item):
        #item의 상태가 변경되었을 때 호출됨
        #그런데 item은 무조건 open에서 시작하므로 여기에 호출되는 item은
        #open이 아닌 값을 가지게 된다.
        #즉 여기에 호출되는 값들은 cancel, done 둘 중 하나 이다
        #change item : {'uuid': 'd914abb5-de18-497c-a34a-95e66edece8d', 'side': 'ask', 'ord_type': 'limit', 'price': '1000000.0', 'state': 'cancel', 'market': 'KRW-IQ', 'created_at': '2019-06-21T23:37:06+09:00', 'volume': '1000.0', 'remaining_volume': '1000.0', 'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '0.0', 'locked': '1000.0', 'executed_volume': '0.0', 'trades_count': 0}
        if(item['state'] == 'cancel'):
            print('change item : {}'.format(item))
        #cancel order
        uuid = item['uuid']
        ot.upbit.cancel_private_order(uuid)
        
        print('-'*120)
        print('-'*120)
        print('event trigger with {}'.format(item))
        print('-'*120)
        print('-'*120)
      
    try:
        msg, order = ot.upbit.create_order('IQ/KRW', 'limit', 'sell', '1000', '1000000', '')
        #{'symbol': 'IQ/KRW', 'id': 'd914abb5-de18-497c-a34a-95e66edece8d', 'side': 'sell', 'price': 1000000.0, 'amount': 1000.0, 'status': 'open', 'remaining': 1000.0, 'ts_create': 1561127826000, 'ts_updated': None}
        print(order)
    except Exception as exp:
        print(exp)
    
    import exchangem.model.order_info
    order1 = exchangem.model.order_info.OrderInfo()
    order1.set('IQ/KRW', 'd914abb5-de18-497c-a34a-95e66edece8d', 'sell', 1000000.0, 1000.0, 'open', 1000.0,1561127826000, None, 'UPBIT', 'test_code')
    
    # 캔슬된 ID
    # order = {'symbol': 'IQ/KRW', 'id': 'd914abb5-de18-497c-a34a-95e66edece8d', 'side': 'sell', 'price': 1000000.0, 'amount': 1000.0, 'status': 'open', 'remaining': 1000.0, 'ts_create': 1561127826000, 'ts_updated': None}
    # item={}
    # item.update(order)
    etc = {
        'callback' : callback
    }
    order['etc'] = etc
    order1['etc'] = etc
    
    print(order)
    
    ot.add_order(order)
    ot.add_order(order1)
    while True:
        time.sleep(60)
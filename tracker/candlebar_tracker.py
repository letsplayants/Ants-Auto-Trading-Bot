# -*- coding: utf-8 -*-
import logging
import threading
import time
import traceback
import sys

import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

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

class CandleBarTracker(BaseClass, metaclass=Singleton):
    """
    등록 된 각 시간별 캔들의 open, close 이벤트가 발생할 때 콜백 함수를 불러준다
    monitoring_list = {
        '1m':{
            'open'  : [[callback_func1, args], ]
            'close' : [[callback_func1, args], ]
        },
        '3m':{
            'open'  : [[callback_func1, args], ]
            'close' : [[callback_func1, args], ]
        },
        '5m':{
            'open'  : [[callback_func1, args], ]
            'close' : [[callback_func1, args], ]
        },
        '60m':{
            'open'  : [[callback_func1, args], ]
            'close' : [[callback_func1, args], ]
        },
        '120m':{
            'open'  : [[callback_func1, args], ]
            'close' : [[callback_func1, args], ]
        }
    }
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.loop = True
        self.interval = 3
        self.monitoring_list = {}
        self.init_scheduler()
        self.run()
    
    def get_zero_hour(self):
        now = time.gmtime(time.time())
        y=now.tm_year 
        m=now.tm_mon 
        d=now.tm_mday
        zero_time = datetime(y, m ,d)
        return zero_time
    
    def __run__(self):
        self.logger.info('scheduler thread start')
        while self.loop:
            
            try:
                self.sched.start()
                while self.loop:
                    time.sleep(1)
            except Exception as exp:
                self.logger.error('scheduler has error!')
            
        self.logger.info('scheduler thread finish')
                
    def run(self):
        self.thread_hnd = threading.Thread(target=self.__run__, args=())
        self.thread_hnd.start()
    
    def stop(self):
        self.logger.info('Call scheduler thread stop func')
        self.loop = False
        for key in self.available_key_list:
            self.sched.remove_job(key)
        self.sched.shutdown()
        self.thread_hnd.join()
    
    def init_scheduler(self):
        self.sched = BackgroundScheduler()
        
        self.available_key_list = ['1m','5m','10m','15m','30m','45m','60m','120m','180m','240m','300m','360m','480m','720m','1440m']
        s_date = self.get_zero_hour()
        for key in self.available_key_list:
            minute = int(key[:len(key)-1])
            self.sched.add_job(self.job_function, 'interval', args=[key], start_date=s_date, id=key, minutes=minute)
            self.monitoring_list[key] = {}
            self.monitoring_list[key]['open'] = []
            self.monitoring_list[key]['close'] = []
    
        
    def job_function(self, key):
        for item in self.monitoring_list[key]['open']:
            try:
                item[0](item[1])
            except Exception as exp:
                err_str = traceback.format_exc()
                self.logger.warning('Exception in schedule job : \t{}\n{}'.format(exp, err_str))
                traceback.print_tb(exp.__traceback__)
        
        for item in self.monitoring_list[key]['close']:
            try:
                item[0](item[1])
            except Exception as exp:
                err_str = traceback.format_exc()
                self.logger.warning('Exception in schedule job : \t{}\n{}'.format(exp, err_str))
                

    def add_event(self, time_minitue, isopen, callback, args):
        """
        '1m':{
            'open'  : [[callback_func1, args], ]
            'close' : [[callback_func1, args], ]
        },
        """
        key = f'{time_minitue}m'
        if(key not in self.available_key_list):
            raise Exception('time_minute is not support : {}'.format(key))
            
        item = self.monitoring_list.get(key) if self.monitoring_list.get(key) is not None else {}
        if(isopen):
            if(item.get('open') is None):
                item['open'] = []
            item['open'].append([callback, args])
        else:
            if(item.get('close') is None):
                item['close'] = []
            item['close'].append([callback, args])
            
        self.monitoring_list[key] = item
        
    def remove_event(self, time_minute, isopen, uuid):
        key = f'{time_minute}m'
        item = self.monitoring_list.get(key) if self.monitoring_list.get(key) is not None else {}
        if(item is None):
            self.logger.warning('item is not exist')
            return
        
        __list__ = None
        if(isopen):
            __list__ = item.get('open')
        else:
            __list__ = item.get('close')
            
        if(__list__ is None):
            self.logger.warning(f'{time_minute}/{isopen} is not exist')
            return
        
        """
        '1m':{
            'open'  : [[callback_func1, args], ]
            'close' : [[callback_func1, args], ]
        },
        """
        for item in __list__:
            args = item[1]
            if(args['id'] == uuid):
                __list__.remove(item)
                return
            
        self.logger.warning(f'{time_minute}/{isopen}/{uuid} is not exist')
    
    
    
        
        
if __name__ == '__main__':
    print('CandleBarTracker test')
    
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
    
    ct = CandleBarTracker()
    
    def myFunc(args):
        # Working with local variables only is thread safe.
        print('call myFunc - {}'.format(args))
        raise Exception('e')
        
    from exchangem.model.order_info import OrderInfo
    item = OrderInfo()
    item.set('BTC/KRW', 'abc-def1', 'limit', '1000000', '1', 'open', 0, 1, 2, 'upbit', 'from_test')
    ct.add_event(1, False, myFunc, item)
    
    item = OrderInfo()
    item.set('BTC/KRW', 'abc-def2', 'limit', '1000000', '3', 'open', 0, 1, 2, 'upbit', 'from_test')
    ct.add_event(5, False, myFunc, item)
    
    item = OrderInfo()
    item.set('BTC/KRW', 'abc-def3', 'limit', '1000000', '5', 'open', 0, 1, 2, 'upbit', 'from_test')
    ct.add_event(10, False, myFunc, item)
    
    item = OrderInfo()
    item.set('BTC/KRW', 'abc-def4', 'limit', '1000000', '10', 'open', 0, 1, 2, 'upbit', 'from_test')
    ct.add_event(15, False, myFunc, item)
    
    item = OrderInfo()
    item.set('BTC/KRW', 'abc-def3', 'limit', '1000000', '1', 'open', 0, 1, 2, 'upbit', 'from_test')
    ct.remove_event(45, False, 'abc-def3')
    
    
    ct.job_function('1m')
    
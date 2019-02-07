# -*- coding: utf-8 -*-
import alogger
import logging
from provider.data_provider import DataProvider
from strategies.arbitage.strategy import StrategyTypeA

class Worker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass
    
    def run(self):
        self.logger.info('run')
        
        #사용할 전략을 만든다
        self.strategy = StrategyTypeA()
        
        #전략에서 필요로 하는 모듈들을 선언
        self.data_provider = DataProvider()
        
        #전략에서 사용할 데이터 제공자를 등록
        self.strategy.register_data_provider(self.data_provider)
        
        #데이터 제공자를 실행한다
        self.data_provider.run()
        
        #전략을 실행한다
        self.strategy.run()
        
    def do_action(self, order):
        self.logger.info('do_action using order book')
        
        #order를 사용하여 액션을 한다
        # self.exchange
        
        #action을 한 후 action 모니터링 큐에 넣는다.
        self.exchange_repoter(order_id)
        
    
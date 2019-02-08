# -*- coding: utf-8 -*-
import logging
from ants.provider.observers import Observer

class EmailAlretStrategy(Observer):
    """
    Email에 메일이 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
    
    def run(self):
        self.logger.info('strategy run')
        
        
    def register_data_provider(self, provider):
        self.data_provider = provider

    def __perform(self, obu):
        #obu을 사용하여 판정을 한다
        #판정 후 등록된 func를 호출한다
        self.logger.info('perform strategy')
        
    def update(self, args):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy')
        print(args)
        pass
    
    def stop(self):
        self.logger.info('Strategy will stop')
        
    
if __name__ == '__main__':
    print('test')
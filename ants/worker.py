# -*- coding: utf-8 -*-
import logging
import alogger
import importlib
import ants.utils as utils
from ants.strategies.mq_strategy import MQStrategy 

class Worker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strategy = []
        #설정파일을 읽어들인다.
        config = utils.readConfig('configs/ants.conf')
    
        try:
            for strategy_item in config['strategy']['strategy']:
                strategy_path = 'ants.strategies.' + strategy_item
                strategy_class = strategy_path[strategy_path.rindex('.') + 1:]
                strategy_path = strategy_path[:strategy_path.rindex('.')]
                self.logger.debug('strategy_path : {}'.format(strategy_path))
                self.logger.debug('strategy_lcass : {}'.format(strategy_class))
    
                try:
                    #전략에 사용할 설정 파일을 읽어들인다
                    self.strategy_config = config['strategy']['config']
                except:
                    self.strategy_config = None
                self.logger.debug('strategy_config : {}'.format(self.strategy_config))
                
                #사용할 전략을 만든다
                loaded_module = importlib.import_module(strategy_path)
                klass = getattr(loaded_module, strategy_class)
                self.strategy.append(klass({'config': self.strategy_config, }))
                
                self.logger.info('USING STRATEGY {}'.format(klass))
        except Exception as exp:
            msg = 'Can''t load strategy : \n{}'.format(exp)
            self.logger.error(msg)
            raise Exception(msg)
        
        pass
    
    def run(self):
        self.logger.info('run')
        
        #전략을 실행한다
        for strategy in self.strategy:
            strategy.run()
        
    def do_action(self, order):
        self.logger.info('do_action using order book')
        
        #order를 사용하여 액션을 한다
        # self.exchange
        
        #action을 한 후 action 모니터링 큐에 넣는다.
        self.exchange_repoter(order_id)
    
    def stop(self):
        for strategy in self.strategy:
            strategy.stop()
    
if __name__ == '__main__':
    print('worker test')
    from telegram_repoter import TelegramRepoter
    tel = TelegramRepoter()
    
    w = Worker()
    w.run()
    
    
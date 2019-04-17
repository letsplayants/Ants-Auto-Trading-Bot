# -*- coding: utf-8 -*-
import logging

import ants.strategies.strategy
from ants.provider.observers import Observer
from ants.provider.rabbitmq_rcv import MQProvider
from ants.performer.smart_trader import SmartTrader

from exchangem.exchanges.upbit import Upbit as cUpbit
from exchangem.exchanges.bithumb import Bithumb as cBithumb
from exchangem.exchanges.binance import Binance as cBinance
from exchangem.database.sqlite_db import Sqlite

from messenger.q_publisher import MQPublisher

class MQStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    MQ 메시지가 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.telegram_messenger_exchange_name = 'messenger.telegram.message'
        self.messenger_q = MQPublisher(self.telegram_messenger_exchange_name)
        
        self.trader = SmartTrader()
        self.db = None
        
        self.upbit = cUpbit({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/upbit.conf', 'telegram': None, 'db':self.db})
        self.trader.add_exchange('UPBIT', self.upbit)
        
        # self.bithumb = cBithumb({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/bithumb.conf', 'telegram': self.telegram, 'db':self.db})
        # self.trader.add_exchange('BITHUMB', self.bithumb)
        
        # self.binance = cBinance({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/binance.conf', 'telegram': self.telegram, 'db':self.db})
        # self.trader.add_exchange('BINANCE', self.binance)
    
    def run(self):
        #전략에서 사용할 데이터 제공자를 등록 후 실행
        self.data_provider = MQProvider()
        self.data_provider.attach(self)
        self.data_provider.run()
        
        self.logger.info('strategy run')
        
        
    def register_data_provider(self, provider):
        self.data_provider = provider
        self.data_provider.attach(self)
    
    
    def update(self, msg):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy')
        self.do_action(msg)
        pass
    
    def stop(self):
        self.telegram.stop_listener()
        self.data_provider.stop()
        self.logger.info('Strategy will stop')
    
    def do_action(self, msg):
        version = msg['version']
        action = msg['action']
        exchange = msg['exchange']
        market = msg['market']
        coin_name = msg['coin']
        price = msg['price']
        amount = msg['seed']
        
        symbol = coin_name + '/' + market
        self.logger.info('Try Action {} {}/{} {}'.format(exchange, coin_name, market, action))
        try:
            availabel_size = self.trader.get_balance(exchange, coin_name, market, False)
        except Exception as exp:
            self.logger.warning('Trading was failed : {}'.format(exp))
            return
        
        result = self.trader.trading(exchange, market, action, coin_name, price, amount)
        if(result == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            return
        
        self.logger.info('Action Done {}'.format(result))
        self.messenger_q.send('요청하신 내용을 완료하였습니다.\n{}'.format(result))
        
    
if __name__ == '__main__':
    print('strategy test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    
    mq = MQStrategy()
    mq.run()
    msg = {'market': 'VET/USDT', 'time': '10M', 'action': 'SELL', 'exchange': 'BINANCE'}
    # mq.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    # mq.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'BITHUMB'}
    # mq.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    # mq.do_action(msg)
    
    # print('try sell-------------------------------------------------------------------')
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # mq.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # mq.do_action(msg)
    
    msg = {'market': 'XRP/BNB', 'time': '10M', 'action': 'BUY', 'exchange': 'BINANCE'}
    # mq.new_do_action(msg)
    
    msg = {'market': 'XRP/BNB', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # mq.new_do_action(msg)
    
    # exchange, market, action, coin
    # mq.save_state('UPBIT', 'BTC', 'KRW', 'BUY')
    # print('----------------------RESULT : ', mq.get_state('UPBIT', 'BTC', 'KRW'))
    
    # mq.save_state('UPBIT', 'BTC', 'KRW', 'SELL')
    # print('----------------------RESULT : ', mq.get_state('UPBIT', 'BTC', 'KRW'))
    
    # mq.save_state('UPBIT', 'BTC', 'KRW', 'BUY')
    # mq.save_state('BITHUMB', 'BTC', 'KRW', 'BUY')
    # mq.save_state('UPBIT', 'BTC', 'KRW', 'SELL')
    # print('----------------------RESULT : ', mq.get_state('BITHUMB', 'BTC', 'KRW'))
    
    print('-'*160)
    # mq.telegram.stop_listener()
    
    
# -*- coding: utf-8 -*-
import logging

import ants.strategies.strategy
from ants.provider.observers import Observer
from ants.provider.email_provider import EmailProvider
from ants.performer.smart_trader import SmartTrader

from exchangem.exchanges.upbit import Upbit as cUpbit
from exchangem.exchanges.bithumb import Bithumb as cBithumb
from exchangem.exchanges.binance import Binance as cBinance
from exchangem.database.sqlite_db import Sqlite
from exchangem.telegram_repoter import TelegramRepoter

class EmailAlretStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    Email에 메일이 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.actionState = 'READY'  #BUY, SELL, READY
        self.states = {}
        
        self.trader = SmartTrader()
        self.telegram = TelegramRepoter()
        self.db = Sqlite()
        
        self.upbit = cUpbit({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/upbit.conf', 'telegram': self.telegram, 'db':self.db})
        self.trader.add_exchange('UPBIT', self.upbit)
        
        self.bithumb = cBithumb({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/bithumb.conf', 'telegram': self.telegram, 'db':self.db})
        self.trader.add_exchange('BITHUMB', self.bithumb)
        
        self.binance = cBinance({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/binance.conf', 'telegram': self.telegram, 'db':self.db})
        self.trader.add_exchange('BINANCE', self.binance)
    
    def run(self):
        #전략에서 사용할 데이터 제공자를 등록 후 실행
        self.data_provider = EmailProvider()
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
        self.new_do_action(msg)
        pass
    
    def stop(self):
        self.data_provider.stop()
        self.logger.info('Strategy will stop')
    
    def new_do_action(self, msg):
        try:
            exchange = msg['exchange'].upper()
            coin_name = msg['market'].split('/')[0]
            market = msg['market'].split('/')[1]
            action = msg['action'].upper()
        except :
            self.logger.warning('msg format is wrong : {}'.format(msg))
            return
        
        self.logger.info('Try Action {} {}/{} {}'.format(exchange, coin_name, market, action))
        try:
            availabel_size = self.trader.get_balance(exchange, coin_name, market)
        except Exception as exp:
            self.logger.warning('Trading was failed : {}'.format(exp))
            return
        
        if(action.upper() == 'BUY'):
            if(availabel_size > 0):
                self.logger.info('\'BUY\' Signal will ignore cause balance is enought {} {}'.format(coin_name, availabel_size))
                return
        
        result = self.trader.trading(exchange, market, action, coin_name)
        if(result == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            return
        
        self.logger.info('Action Done {}'.format(result))
        
        
    def do_action(self, msg):
        try:
            exchange = msg['exchange'].upper()
            coin_name = msg['market'].split('/')[0]
            market = msg['market'].split('/')[1]
            action = msg['action'].upper()
        except :
            self.logger.warning('msg format is wrong : {}'.format(msg))
            return
        
        self.logger.info('Try Action {} {}/{} {}'.format(exchange, coin_name, market, action))
        
        if(self.get_state(exchange, coin_name, market) == action):
            self.logger.info('Already {} {}/{} {} state'.format(exchange, coin_name, market, action))
            return
        
        result = self.trader.trading(exchange, market, action, coin_name)
        if(result == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            return
        
        self.save_state(exchange, coin_name, market, action)
        self.logger.info('Done Action {} {}/{} {}'.format(exchange, coin_name, market, action))

    def save_state(self, exchange, coin, market, action):
        record = {
            'coin' : coin,
            'market' : market,
            'exchange' : exchange,
            'action' : action
        }
        """
        {
            'upbit': {
                'xrp': {
                    'krw': {
                        'action' : 'buy'
                    },
                    'btc' : {
                        'action' : 'sell'
                    },
                    'usdt' : {
                        'action' : 'buy
                    }
                },
                'trx': {
                    'krw': {
                        'action' : 'buy'
                    },
                    'btc' : {
                        'action' : 'sell'
                    },
                    'usdt' : {
                        'action' : 'buy
                    }
                }
            },
            'bithumb' : {},
            'binance' : {}
        }
        """
        
        ex_rec = self.__get_dict(self.states, exchange)
        coin_rec = self.__get_dict(ex_rec, coin)
        market_rec = self.__get_dict(coin_rec, market)
        market_rec = {'action' : action}
        
        coin_rec[market] = market_rec
        ex_rec[coin] = coin_rec
        self.states[exchange] = ex_rec
        
        
    def __get_dict(self, p, name):
        r = p.get(name)
        if(r == None):
            p[name] = {}
        
        return p[name]
    
    def get_state(self, exchange, coin, market):
        try:
            return self.states[exchange][coin][market]['action']
        except Exception as e:
            self.logger.debug('{} {}/{} has not states : {}'.format(exchange, coin, market, e))
            return None
    
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
    
    st = EmailAlretStrategy()
    # st.run()
    msg = {'market': 'VET/USDT', 'time': '10M', 'action': 'SELL', 'exchange': 'BINANCE'}
    # st.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'BITHUMB'}
    # st.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    # st.do_action(msg)
    
    # print('try sell-------------------------------------------------------------------')
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # st.do_action(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # st.do_action(msg)
    
    msg = {'market': 'XRP/BNB', 'time': '10M', 'action': 'BUY', 'exchange': 'BINANCE'}
    # st.new_do_action(msg)
    
    msg = {'market': 'XRP/BNB', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # st.new_do_action(msg)
    
    # exchange, market, action, coin
    # st.save_state('UPBIT', 'BTC', 'KRW', 'BUY')
    # print('----------------------RESULT : ', st.get_state('UPBIT', 'BTC', 'KRW'))
    
    # st.save_state('UPBIT', 'BTC', 'KRW', 'SELL')
    # print('----------------------RESULT : ', st.get_state('UPBIT', 'BTC', 'KRW'))
    
    # st.save_state('UPBIT', 'BTC', 'KRW', 'BUY')
    # st.save_state('BITHUMB', 'BTC', 'KRW', 'BUY')
    # st.save_state('UPBIT', 'BTC', 'KRW', 'SELL')
    # print('----------------------RESULT : ', st.get_state('BITHUMB', 'BTC', 'KRW'))
    
    
# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from datetime import timedelta

import ants.strategies.strategy
from ants.provider.observers import Observer
from ants.performer.smart_trader import SmartTrader
from ants.provider.email_provider import EmailProvider

from exchangem.exchanges.upbit import Upbit as cUpbit
from exchangem.exchanges.bithumb import Bithumb as cBithumb
from exchangem.exchanges.binance import Binance as cBinance
from exchangem.database.sqlite_db import Sqlite
from exchangem.telegram_repoter import TelegramRepoter

class HanGunStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    한군 전용 전략
    Email에 메일이 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
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

    def update(self, msg):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy : {}'.format(msg))
        self.check_signal(msg)
        pass
    
    def stop(self):
        self.data_provider.stop()
        self.logger.info('Strategy will stop')
    
    def check_signal(self, msg):
        try:
            exchange = msg['exchange'].upper()
            coin_name = msg['market'].split('/')[0]
            market = msg['market'].split('/')[1]
            action = msg['action'].upper()
        except :
            self.logger.warning('msg format is wrong : {}'.format(msg))
            return
        
        state = self.get_state(exchange, coin_name, market)
        
        if(state == None or state == 'READY'):
            self.do_action(msg)
        elif(state == 'BUY'):
            if(action == 'BUY'):
                self.do_action(msg, True)
            elif(action == 'SELL'):
                self.do_action(msg)
        elif(state == '2ND_BUY'):
            if(action == 'BUY'):
                self.logger.warning('This signal({}) will be ignore cause last signal : {}'.format(action, state))
                return
            elif(action == 'SELL'):
                self.do_action(msg)
            
        
    def do_action(self, msg, second_buy=False):
        print('do action : {}'.format(msg))
        try:
            exchange = msg['exchange'].upper()
            coin_name = msg['market'].split('/')[0]
            market = msg['market'].split('/')[1]
            action = msg['action'].upper()
        except :
            self.logger.warning('msg format is wrong : {}'.format(msg))
            return
        
        result = self.trader.trading(exchange, market, action, coin_name)
        if(result == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            return
        
        if(action == 'SELL'):
            action = 'READY'
        if(second_buy):
            action = '2ND_BUY'
            self.logger.info('2ND BUY done')
            
        self.save_state(exchange, coin_name, market, action)
        
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
    logging.getLogger("telegram").setLevel(logging.WARNING)
    
    st = HanGunStrategy()
    # st.run()
    
    # print('SELL Fail-------------------------------------------------------------------')
    # msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # st.update(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    st.update(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    st.update(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'ETH/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    st.update(msg)
    
    # print('BUY BUY BUY SELL-------------------------------------------------------------------')
    # msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    # st.update(msg)
    # msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    # st.update(msg)
    # msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    # st.update(msg)
    # msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # st.update(msg)
    
    
    
    # print('try sell-------------------------------------------------------------------')
    # msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # st.do_action(msg)
    
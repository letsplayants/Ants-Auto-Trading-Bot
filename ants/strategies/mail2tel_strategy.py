# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from datetime import timedelta

import ants.strategies.strategy
from ants.provider.observers import Observer
from ants.provider.email_provider import EmailProvider

from messenger.q_publisher import MQPublisher
from env_server import Enviroments

class Mail2QuickTradingStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    Email에 메일이 수신되면 텔레그램의 Quick Trading 포멧으로 던져준다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.telegram_messenger_exchange_name = Enviroments().qsystem.get_telegram_messenge_q()
        self.messenger_q = MQPublisher(self.telegram_messenger_exchange_name)
    
    def run(self):
        #전략에서 사용할 데이터 제공자를 등록 후 실행
        self.data_provider = EmailProvider(True)
        self.data_provider.attach(self)
        self.data_provider.run()
        
        self.logger.info('strategy run')

    def update(self, msg):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy : {}'.format(msg))
        # 텔레그램으로 메시지를 날려준다
        
        msg=msg[msg.find(':')+2:]
        self.messenger_q.send('{}'.format(msg))
        # self.check_signal(msg)
        pass
    
    def stop(self):
        self.telegram.stop_listener()
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
    
    # st = Mail2QuickTradingStrategy()
    # st.run()
    
    
    
    s='TradingView Alert: sell upbit krw btc 0% 100%'
    s=s[s.find(':')+2:] #header 제거
    _list = s.split()
    print()
    
    
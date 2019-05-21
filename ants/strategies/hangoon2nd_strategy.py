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
        
        if(self.check_signal(msg)):
            self.messenger_q.send('{}'.format(msg))
        
        pass
    
    def stop(self):
        self.telegram.stop_listener()
        self.data_provider.stop()
        self.logger.info('Strategy will stop')
    
    def check_signal(self, msg):
        """
        세번째 buy일 경우 false
        그 외 true
        """
        text = msg.split(' ')
        
        command = text[0].strip().upper()
        exchange = text[1].strip().upper()
        market = text[2].strip().upper()
        coin_name = text[3].strip().upper()
        
        if(command == 'BUY'):
            buy_cnt = self.get_state(exchange, coin_name, market)
            buy_cnt += 1
            if(buy_cnt > 2):
                return False
        elif(command == 'SELL'):
            buy_cnt = 0
        
        self.save_state(exchange, coin_name, market, 'buy', buy_cnt)
        
        return True
   
    def save_state(self, exchange, coin, market, action, buy_cnt):
        class_name = self.__class__.__name__.lower()
        
        # 기존 데이터를 읽어서 거기에 애드한다
        record_strategy = self.__get_dict__(Enviroments().strategies, class_name)
        record_exchange = self.__get_dict__(record_strategy, exchange)
        record_coin = self.__get_dict__(record_exchange, coin)
        record_market = self.__get_dict__(record_coin, market)
        
        record_market['buy_cnt'] = buy_cnt
        record_coin[market] = record_market
        record_exchange[coin] = record_coin
        record_strategy[exchange] = record_exchange
        
        Enviroments().strategies[class_name] = record_strategy
        Enviroments().save_config()
        
    def __get_dict__(self, p, name):
        r = p.get(name)
        if(r == None):
         p[name] = {}
        
        return p[name]

    def get_state(self, exchange, coin, market):
        try:
            class_name = self.__class__.__name__.lower()
            cnt = Enviroments().strategies[class_name][exchange][coin][market]
            return cnt['buy_cnt']
        except Exception as e:
            self.logger.debug('{} {}/{} has not states : {}'.format(exchange, coin, market, e))
            return 0
    
if __name__ == '__main__':
    print('strategy test')
    
    import os
    path = os.path.dirname(__file__) + '../../configs/ant_auto.conf'
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
    
    
    s='TradingView Alert: sell upbit krw btc 0% 100%'
    s=s[s.find(':')+2:] #header 제거
    _list = s.split()
    print()
    
    test = Mail2QuickTradingStrategy()
    # test.save_state('upbit','btc','krw','buy',0)
    # test.save_state('upbit','eth','krw','buy',1)
    # test.save_state('binance','eth','btc','buy',1)
    # test.save_state('binance','xrp','btc','buy',1)
    # test.save_state('bithumb','btc','krw','buy',1)
    
    # state = test.get_state('upbit', 'eth', 'krw')
    # print(state)
    #------------------------------------------
    print('2 buy test')
    msg ='buy upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('1 do buy')
    
    msg ='buy upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('2 do buy')
        
    msg ='buy upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('3 do buy')
    
    msg ='sell upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('1 do sell')
        
    msg ='buy upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('1 do buy')
    
    msg ='sell upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('1 do sell')
    
    #------------------------------------------
    print('complex buy test')
    msg ='buy upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('BTC 1 do buy')
    
    msg ='buy upbit krw eth 0% 100%'
    if(test.check_signal(msg)):
        print('ETH 1 do buy')
        
    msg ='buy upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('BTC 2 do buy')
    
    msg ='buy upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('BTC 3 do buy')
    
    msg ='sell upbit krw btc 0% 100%'
    if(test.check_signal(msg)):
        print('BTC 1 do sell')
        
    msg ='buy upbit krw eth 0% 100%'
    if(test.check_signal(msg)):
        print('eth 2 do buy')
    
    msg ='buy upbit krw eth 0% 100%'
    if(test.check_signal(msg)):
        print('eth 3 do buy')
        
    msg ='sell upbit krw eth 0% 100%'
    if(test.check_signal(msg)):
        print('eth 1 do sell')
    
    
    
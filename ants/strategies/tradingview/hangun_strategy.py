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

class HanGunStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    한군 전용 전략
    Email에 메일이 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.actionState = 'READY'  #BUY, SELL, READY
        self.cooldown = 55  #minitue
        self.actionTime = datetime.now() - timedelta(minutes=self.cooldown)
        self.trader = SmartTrader()
        
        self.upbit = cUpbit({'private_key_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/upbit.conf'})
        self.trader.add_exchange('UPBIT', self.upbit)
        
        self.bithumb = cBithumb({'private_key_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/bithumb.conf'})
        self.trader.add_exchange('BITHUMB', self.bithumb)
        
        self.binance = cBinance({'private_key_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/binance.conf'})
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
        self.logger.debug('got msg in data strategy')
        self.check_signal(msg)
        pass
    
    def stop(self):
        self.logger.info('Strategy will stop')
    
    def check_signal(self, msg):
        try:
            action = msg['action'].upper()
        except Exception as ex:
            self.logger.warning('Can''t get action : {}'.format(ex))
            return;
        
        current = datetime.now()
        timeGap = self.actionTime + timedelta(minutes=self.cooldown)
        if(current < timeGap):
            self.logger.debug('{} signal ignore cause now is cooldown'.format(action))
            return
        
        if(self.actionState == 'READY'):
            if(action == 'SELL'):
                return
            elif(action == 'BUY'):
                self.do_action(msg)
        elif(self.actionState == 'BUY'):
            if(action == 'BUY'):
                self.do_action(msg, True)
            elif(action == 'SELL'):
                self.do_action(msg)
        elif(self.actionState == '2ND_BUY'):
            if(action == 'BUY'):
                return
            elif(action == 'SELL'):
                self.do_action(msg)
            
        
    def do_action(self, msg, second_buy=False):
        try:
            exchange = msg['exchange'].upper()
            coinName = msg['market'].split('/')[0]
            market = msg['market'].split('/')[1]
            action = msg['action'].upper()
        except :
            self.logger.warning('msg format is wrong : {}'.format(msg))
            return
        
        result = self.trader.trading(exchange, market, action, coinName)
        if(result == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            return
        
        if(action == 'SELL'):
            action = 'READY'
        if(second_buy):
            action = '2ND_BUY'
            self.logger.info('2ND BUY done')
            
        self.actionState = action
        self.actionTime = datetime.now()
        

    
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
    
    st = HanGunStrategy()
    
    # print('SELL Fail-------------------------------------------------------------------')
    # msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
    # st.update(msg)
    
    print('BUY SELL-------------------------------------------------------------------')
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'BUY', 'exchange': 'UPBIT'}
    st.update(msg)
    msg = {'market': 'BTC/KRW', 'time': '10M', 'action': 'SELL', 'exchange': 'UPBIT'}
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
    
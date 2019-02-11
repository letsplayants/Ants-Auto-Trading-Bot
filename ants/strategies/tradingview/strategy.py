# -*- coding: utf-8 -*-
import logging
from ants.provider.observers import Observer
from ants.performer.smart_trader import SmartTrader
from exchangem.exchanges.upbit import Upbit as cUpbit
from exchangem.exchanges.bithumb import Bithumb as cBithumb

class EmailAlretStrategy(Observer):
    """
    Email에 메일이 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.actionState = 'READY'  #BUY, SELL, READY
        self.trader = SmartTrader()
        
        self.upbit = cUpbit({'key_file':'configs/upbit.key', 'config_file':'configs/upbit.conf'})
        self.trader.add_exchange('UPBIT', self.upbit)
        
        self.bithumb = cBithumb({'key_file':'configs/bithumb.key', 'config_file':'configs/bithumb.conf'})
        self.trader.add_exchange('BITHUMB', self.bithumb)
    
    def run(self):
        self.logger.info('strategy run')
        
        
    def register_data_provider(self, provider):
        self.data_provider = provider
        self.data_provider.attach(self)

    def __perform(self, obu):
        #obu을 사용하여 판정을 한다
        #판정 후 등록된 func를 호출한다
        self.logger.info('perform strategy')
        
    def update(self, msg):
        """
        데이터 제공자가 요청한 데이터가 수신되면 호출한다
        """
        self.logger.debug('got msg in data strategy')
        self.do_action(msg)
        pass
    
    def stop(self):
        self.logger.info('Strategy will stop')
    
    def do_action(self, msg):
        exchange = msg['exchange'].upper()
        coinName = msg['market'][0:3].upper()
        market = msg['market'][3:6].upper()
        action = msg['action'].upper()
        
        if(self.actionState == action) :
            self.logger.info('Already {} state'.format(action))
            return
        
        result = self.trader.trading(exchange, market, action, coinName)
        if(result == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            return
        
        self.actionState = action

    
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
    msg = {'market': 'BTCKRW', 'time': '10M', 'action': 'BUY', 'exchange': 'BITHUMB'}
    # st.do_action(msg)
    
    print('try sell-------------------------------------------------------------------')
    msg = {'market': 'BTCKRW', 'time': '10M', 'action': 'SELL', 'exchange': 'BITHUMB'}
    st.do_action(msg)
    
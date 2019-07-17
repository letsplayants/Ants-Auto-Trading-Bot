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
from env_server import Enviroments

class MQStrategy(ants.strategies.strategy.StrategyBase, Observer):
    """
    MQ 메시지가 수신되면 거기에 맞춰서 거래를 하도록 한다
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.data_provider = None
        self.telegram_messenger_exchange_name = Enviroments().qsystem.get_telegram_messenge_q()
        self.messenger_q = MQPublisher(self.telegram_messenger_exchange_name)
        
        self.trader = SmartTrader()
        self.db = None
        
        self.upbit = cUpbit()
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
        self.data_provider.stop()
        self.logger.info('Strategy will stop')
    
    def trading(self, msg):
        try:
            version = msg['version']
            command = msg['command']
            exchange = msg['exchange']
            market = msg['market']
            coin_name = msg['coin']
            price = msg['price']
            amount = msg['seed']
            rule = msg['rule']
            etc = msg['etc']
        except Exception as exp:
            self.logger.warning('msg parsing error : {}'.format(exp))
            return
            
        symbol = coin_name + '/' + market
        self.logger.info('Try Action {} {}/{} {}'.format(exchange, coin_name, market, command))
        # try:
        #     availabel_size = self.trader.get_balance(exchange, coin_name, market, False)
        # except Exception as exp:
        #     self.logger.warning('Trading was failed : {}'.format(exp))
        #     return
        
        try:
            message, order_info = self.trader.trading(exchange, market, command, coin_name, price, amount, etc)
            #results는 ['msg']와 ['order_info']로 나눠져서 들어온다
            #order_info는 오더를 생성하고 서버에서 받은 정보를 가지고 있다. 즉 오더 id를 가지고 있음
            
            #생성된 오더 정보를 기반으로 추적 시스템에 넣는다
            #오더 분봉에 정보를 가지고 와서 분봉이 close되면 모든 오더가 취소되는 기능을 넣는다
            # message = result['msg']
            # order_info = result['order_info']
            self.logger.debug('trading result : \n{}\n{}'.format(message, order_info))
        except Exception as exp:
            self.messenger_q.send(str(exp))
            self.logger.warning('Trading was failed : {}'.format(exp))
            return
            
        if(order_info == None):
            #트레이딩 실패
            self.logger.warning('Trading was failed')
            self.messenger_q.send('실패 : 요청하신 내용을 실패하였습니다.\n{}'.format(order_info))
            return
        
        self.logger.info('Action Done {}'.format(order_info))
        self.messenger_q.send('요청하신 내용을 완료하였습니다.\n{}\n{}'.format(message, order_info))
        
    def do_action(self, msg):
        try:
            version = msg['version']
            command = msg['command']
        except Exception as exp:
            self.logger.warning('msg parsing error : {}'.format(exp))
            return
        
        if(command in ['BUY', 'SELL']):
            self.trading(msg)
        elif(command in ['SHOW']):
            self.show_order(msg)
        elif(command in ['CANCEL']):
            self.cancel_order(msg)
    
    def cancel_order(self, msg):
        try:
            version = msg['version']
            command = msg['command']
            sub_cmd = msg['sub_cmd']
            exchange = msg['exchange']
            order_id = msg['id']
        except Exception as exp:
            msg = 'cancel order msg parsing error : {}'.format(exp)
            self.logger.warning(msg)
            self.messenger_q.send(msg)
            return
        
        try:
            orders = self.trader.cancel_order(exchange, order_id)
        except Exception as exp:
            self.messenger_q.send('요청하신 작업 중 오류가 발생하였습니다.\n{}'.format(exp))
            return
            
        self.messenger_q.send('주문 취소 성공')
        
    def show_order(self, msg):
        try:
            version = msg['version']
            command = msg['command']
            exchange = msg['exchange']
            sub_cmd = msg['sub_cmd']
            coin_name = msg['coin_name']
            if(coin_name == ''):
                coin_name = None
        except Exception as exp:
            self.logger.warning('msg parsing error : {}'.format(exp))
            return
        
        try:
            orders = self.trader.get_private_orders(exchange)
            order_str = '오더목록\n'
            self.messenger_q.send(order_str)
            for order in orders:
                if(exchange == 'UPBIT'):
                    order_str = self.order_paring(exchange, order, coin_name)
                else:
                    order_str = str(order) + '\n'
                
                if(order_str is not None):
                    self.messenger_q.send(order_str)
            
        except Exception as exp:
            self.messenger_q.send('요청하신 작업 중 오류가 발생하였습니다.\n{}'.format(exp))
            
        self.messenger_q.send('오더 목록 출력 완료')
    
    def order_paring(self, exchange, msg, trg_coin_name=None):
        # {'symbol': 'BTC/KRW', 'id': '23ddd54a-3fa8-4635-aa61-88ad657c1e14', 'side': 'buy', 'price': 0.99, 'amount': 10095.95959596, 'status': 'open', 'remaining': 10095.95959596, 'ts_create': 1555432332000, 'ts_updated': None}
        coin_name = msg['symbol'].split('/')[0]
        market = msg['symbol'].split('/')[1]
        price = float(msg['price'])
        amount = float(msg['amount'])
        pp = price * amount
        side = msg['side']
        if(side == 'buy'):
            side = '구매중'
        elif(side == 'sell'):
            side = '판매중'
        
        if(trg_coin_name is not None and trg_coin_name != coin_name):
            return None
        
        ret = 'SHOW ORDER\n'
        ret = ret + '거래소 : {}\n'.format(exchange)
        ret = ret + 'ID : {}\n'.format(msg['id'])
        ret = ret + '{}\n'.format(side)
        ret = ret + '마켓 : {}\n'.format(market)
        ret = ret + '코인이름 : {}\n'.format(coin_name)
        ret = ret + '단가 : {}\n'.format(price)
        ret = ret + '수량 : {}\n'.format(amount)
        ret = ret + '수량 금액(단가 * 수량) : {}\n'.format(pp)
        
        return ret
    
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
    
    
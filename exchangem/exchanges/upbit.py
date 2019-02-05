# -*- coding: utf-8 -*-
import logging
import time
import json
from datetime import datetime
import websocket
import threading

from model.exchange import Base

class Upbit(Base):
    def __init__(self):
        # super().__init__(self)
        Base.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.chainse = []
        pass
    
    def _order(self, args):
        """
        각 거래소마다 지정된 형태로 오더를 내린다
        ccxt를 사용한다
        """
        pass
    
    def connect(self):
        self.noti_msg( '### 연결 중..')
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                  on_message = lambda ws, msg: self.on_message(ws, msg),
                                  on_error = lambda ws, msg: self.on_error(ws, msg),
                                  on_close = lambda ws: self.on_close(ws),
                                  on_open = lambda ws: self.on_open(ws))
        self.thread_hnd = threading.Thread(target=self.ws.run_forever)
        self.thread_hnd.start()
        
        
    def on_message(self, ws, message):
        # self.logger.debug( 'got message in upbit : {}'.format(message) )
        self.notify(message)
        pass

    def on_error(self, ws, error):
        self.logger.error( error )

    def on_close(self, ws):
        self.logger.info( "### closed ###" )

    def on_open(self, ws):
        data=[{"ticket":"upbit_arbit_bot"}, #고유한 키값을 넣어서 응답이 왔을 때 구분자로 사용한다.
            {"type":"orderbook","codes":self.coins},
            {"format":"SIMPLE"}]
        ws.send(json.dumps(data))
        
    def close(self):
        self.ws.close()
    
    def noti_msg(self, msg):
        self.logger.info(msg)
        # aTeleBot.sendMessageToAll(msg)
    
    def target_coins(self, coins):
        self.coins = coins
    
    def get_order_book(self):
        self.connect()
    
    def register_callback(cb):
        pass
    
if __name__ == '__main__':
    print('test')
    up = Upbit()
    coins = ['KRW-ETH', 'KRW-DASH', 'ETH-DASH', 'KRW-LTC', 'ETH-LTC', 'KRW-STRAT', 'ETH-STRAT', 'KRW-XRP', 'ETH-XRP', 'KRW-ETC', 'ETH-ETC', 'KRW-OMG', 'ETH-OMG', 'KRW-SNT', 'ETH-SNT', 'KRW-WAVES', 'ETH-WAVES', 'KRW-XEM', 'ETH-XEM', 'KRW-ZEC', 'ETH-ZEC', 'KRW-XMR', 'ETH-XMR', 'KRW-QTUM', 'ETH-QTUM', 'KRW-GNT', 'ETH-GNT', 'KRW-XLM', 'ETH-XLM', 'KRW-REP', 'ETH-REP', 'KRW-ADA', 'ETH-ADA', 'KRW-POWR', 'ETH-POWR', 'KRW-STORM', 'ETH-STORM', 'KRW-TRX', 'ETH-TRX', 'KRW-MCO', 'ETH-MCO', 'KRW-SC', 'ETH-SC', 'KRW-POLY', 'ETH-POLY', 'KRW-ZRX', 'ETH-ZRX', 'KRW-SRN', 'ETH-SRN', 'KRW-BCH', 'ETH-BCH', 'KRW-ADX', 'ETH-ADX', 'KRW-BAT', 'ETH-BAT', 'KRW-DMT', 'ETH-DMT', 'KRW-CVC', 'ETH-CVC', 'KRW-WAX', 'ETH-WAX']

    from model.observers import Observer
    class Update(Observer):
        def update(self, args):
            print('got msg in udt')
            pass
    
    udt = Update()
    
    print(Update.mro())
    print('1...')
    up.target_coins(coins)
    print('2...')
    up.attach(udt)
    up.get_order_book()
    print('3...')
    # up.connect()
    
    
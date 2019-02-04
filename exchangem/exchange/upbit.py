# -*- coding: utf-8 -*-
import logging
import time
import json
from datetime import datetime
import websocket
from observers import ObserverNotifier

class Upbit(ObserverNotifier):
    def __init__(self):
        ObserverNotifier.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.chainse = []
        pass
        
    # def on_message(self, ws, message):
    #     self.logger.info('got message: {}'.format(message))
        
    #     data = json.loads(message)
    #     # coin = extract_coin( data['cd'] )
    #     # if 'KRW-ETH' in orderbooks and 'KRW-'+coin in orderbooks and 'ETH-'+coin in orderbooks:
    #     #     # print( coin + " Exist. Can be calculate")
    #     #     orderbooks[ data['cd'] ] = data
    #     #     judge( coin )
    #     # else:
    #     #     # if coin == '':
    #     #     #     print( 'KRW-ETH updated' )
    #     #     # else:
    #     #     #     print( coin + ' not Exist')
    #     #     orderbooks[ data['cd'] ] = data
    
    # def on_error(self, ws, error):
    #     print(error)
    
    # def on_close(self, ws):
    #     self.noti_msg('### 연결 끊어짐 ### ')
    #     # timer = threading.Timer(10, connect)
    #     # timer.start()
    
    # def on_open(self, ws):
    #     self.noti_msg( '### 연결 됨!!')
    #     data=[{"ticket":"upbit_arbit_bot"}, #고유한 키값을 넣어서 응답이 왔을 때 구분자로 사용한다.
    #         {"type":"orderbook","codes":['KRW-BTC']},
    #         {"format":"SIMPLE"}]
    #     ws.send(json.dumps(data))

        # while True:
        #     print("[ " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ] ')
        #     time.sleep(10)

        # ws.close()
        # self.noti_msg("thread terminating...")
    
    
    def connect(self):
        self.noti_msg( '### 연결 중..')
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                  on_message = lambda ws, msg: self.on_message(ws, msg),
                                  on_error = lambda ws, msg: self.on_error(ws, msg),
                                  on_close = lambda ws: self.on_close(ws),
                                  on_open = lambda ws: self.on_open(ws))
        self.ws.run_forever()
        
        
    def on_message(self, ws, message):
        self.logger.debug( 'got message in upbit : {}'.format(message) )
        self.notify(message)
        pass

    def on_error(self, ws, error):
        print( error )

    def on_close(self, ws):
        print( "### closed ###" )

    def on_open(self, ws):
        data=[{"ticket":"upbit_arbit_bot"}, #고유한 키값을 넣어서 응답이 왔을 때 구분자로 사용한다.
            {"type":"orderbook","codes":self.coins},
            {"format":"SIMPLE"}]
        ws.send(json.dumps(data))
        
    def close(self):
        self.ws.close()
    
    def noti_msg(self, msg):
        print(msg)
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

    up.target_coins(coins)
    up.get_order_book()
    # up.connect()
        
    
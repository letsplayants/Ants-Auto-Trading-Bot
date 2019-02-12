# -*- coding: utf-8 -*-

import unittest
import sys
import os
import pkgutil
import ccxt

from exchangem.utils import Util as util


class CcxtTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    # def setUp(self):
        # self.bithumb = Bithumb(self.apiKey, self.apiSecret)

    def tearDown(self):
        pass
    
    # def test_callPubAPI(self):
    #     print(ccxt.exchanges)
        
        
    def get_upbit(self):
        keys = util.readKey('./configs/upbit.key')
        apiKey = keys['apiKey']
        apiSecret = keys['secret']
        
        return ccxt.upbit({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        })
        
    
    def get_bithumb(self):
        keys = util.readKey('./configs/bithumb.key')
        apiKey = keys['apiKey']
        apiSecret = keys['secret']
        
        return ccxt.bithumb({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        })

    def get_binance(self):
        keys = util.readKey('./configs/binance.key')
        apiKey = keys['apiKey']
        apiSecret = keys['secret']
        
        return ccxt.bithumb({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        })

    def get_bitfinex(self):
        keys = util.readKey('./configs/bitfinex.key')
        apiKey = keys['apiKey']
        apiSecret = keys['secret']
        
        return ccxt.bitfinex({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        })
        return bithumb
    
       
    def test_upbit_pub_api(self):
        upbit = ccxt.upbit()
        # print(upbit.id)
        # print(upbit.load_markets())
        
    def test_bithumb_pub_api(self):
        bithumb = ccxt.bithumb()
        # print(bithumb.id)
        # print(bithumb.load_markets())
        
    def test_bithumb_pri_api(self):
        keys = util.readKey('./configs/bithumb.key')
        apiKey = keys['apiKey']
        apiSecret = keys['secret']
        
        bithumb = ccxt.bithumb({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        })
        
        # print(bithumb.fetch_balance())
        
    def test_ccxt_api_test(self):
        # self.get_balance()
        # self.get_order_book()
        # self.get_order()
        # self.get_market_price()
        self.get_fees()
        
    def get_fees(self):
        exchange = self.get_bithumb()
        print(exchange.load_fees())
        
        exchange = self.get_upbit()
        print(exchange.load_fees())
        exchange.calculate_fee()
        
    def get_fee(self):
        # symbol = 'BTC/KRW'
        # type = 'limit'
        # side = 'buy'
        # amount = 1
        # price = 5000000
        # takerOrMaker = 'taker'
        # calculate_fee는 테스트 중인 함수라 사용하지 않는 것을 추천함
        # https://github.com/ccxt/ccxt/wiki/Manual#fees
        # print(exchange.calculate_fee(symbol, type, side, amount, price, takerOrMaker))
        pass
        
    
    def get_order(self):
        #전부 동작안함. 빗썸 업빗 둘 다 지원 안한다고 나옴
        exchange = self.get_bithumb()
        orders = exchange.fetch_orders()
        print(orders)
        order = exchange.fetch_order(orders[0]['id'])
        print(order)

        exchange = self.get_upbit()
        orders = exchange.fetch_orders()
        print(orders)
        order = exchange.fetch_order(orders[0]['id'])
        print(order)
    
    def get_market_price(self):
        symbol='BTC/KRW'
        ex = self.get_bithumb()
        print(ex.fetch_ticker(symbol))
        """
        {'symbol': 'BTC/KRW', 'timestamp': 1549698009141, 'datetime': '2019-02-09T07:40:09.141Z', 'high': 4100000.0, 'low': 3776000.0, 'bid': 4002000.0, 'bidVolume': None, 'ask': 4004000.0, 'askVolume': None, 'vwap': 3927711.3257, 'open': 3778000.0, 'close': 4004000.0, 'last': 4004000.0, 'previousClose': None, 'change': 226000.0, 'percentage': 5.9820010587612495, 'average': 3891000.0, 'baseVolume': 5113.40675249, 'quoteVolume': 20083985614.66583, 'info': {'opening_price': '3778000', 'closing_price': '4004000', 'min_price': '3776000', 'max_price': '4100000', 'average_price': '3927711.3257', 'units_traded': '5113.40675249', 'volume_1day': '5113.40675249', 'volume_7day': '17281.38692642', 'buy_price': '4002000', 'sell_price': '4004000', '24H_fluctate': '226000', '24H_fluctate_rate': '5.98', 'date': '1549698009141'}}
        """
        ex = self.get_upbit()
        ticker = ex.fetch_ticker(symbol)
        print(ticker['last'])
        #last 부분을 읽어들이면 최종 체결가를 알 수 있긴함.
     
    def get_order_book(self):
        ex = self.get_upbit()
        result = ex.fetch_order_books(['ETH/BTC', 'LTC/BTC'])
        print(result)
        
        try:
            ex = self.get_bithumb()
            result = ex.fetch_order_books(['ETH/KRW', 'BTC/KRW'])
            print(result)
        except Exception as e:
            print(e)
        
    
    def get_balance(self):
        exc = self.get_bithumb()
        print('bithumb balance : ')
        print(exc.fetch_balance())
        
        exc = self.get_upbit()
        print('upbit balance : ')
        print(exc.fetch_balance())    
    
    def test_upbit_buy(self):
        upbit = self.get_upbit()
        # print(upbit.load_markets())
        
        # doc sample
        # create_order(self, symbol, type, side, amount, price=None, params={}):
        # $hitbtc->create_order ('BTC/USD', 'limit', 'buy', 1, 3000, array ('clientOrderId' => '123'));
        # print(exmo.id, exmo.create_limit_buy_order('BTC/EUR', 1, 2500.00))
        
        
        try:
            symbol = 'BTC/KRW'
            _type = 'limit'  # or 'market' or 'limit'
            side = 'buy'  # 'buy' or 'sell'
            amount = 0.0
            price = 3900000  # or None
            
            params = {
                # 'test': True,  # test if it's valid, but don't actually place it
                }
    
            desc = upbit.create_order(symbol, _type, side, amount, price, params)
            print(desc)
            """
            desc : {'info': {'uuid': 'e6c58e82-1ddb-4783-8376-3723763e365a', 'side': 'bid', 'ord_type': 'limit', 'price': '3900000.0', 'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2019-02-09T10:07:30+09:00', 'volume': '0.003', 'remaining_volume': '0.003', 'reserved_fee': '5.85', 'remaining_fee': '5.85', 'paid_fee': '0.0', 'locked': '11705.85', 'executed_volume': '0.0', 'trades_count': 0}, 'id': 'e6c58e82-1ddb-4783-8376-3723763e365a', 'timestamp': 1549674450000, 'datetime': '2019-02-09T01:07:30.000Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/KRW', 'type': 'limit', 'side': 'buy', 'price': 3900000.0, 'cost': 0.0, 'average': 3900000.0, 'amount': 0.003, 'filled': 0.0, 'remaining': 0.003, 'status': 'open', 'fee': {'currency': 'KRW', 'cost': 0.0}, 'trades': None}
            """
        except Exception as exp:
            print(exp)
    
    
        
    
    def _test_upbit_sell(self):
        upbit = self.get_upbit()
                        
        try:
            symbol = 'BTC/KRW'
            _type = 'limit'  # or 'market'
            side = 'sell'  # or 'buy'
            amount = 0.0003
            price = 5000000  # or None
            
            params = {
                # 'test': True,  # test if it's valid, but don't actually place it
                }

            #잘못된 파라메터가 들어갈 경우 서버에서 응답 거부를 한다
            #market방식으로 거래할 경우 price부분은 None처리가 가능하다.
            desc = upbit.create_order(symbol, _type, side, amount, price, params)
            print(desc)
            """
            desc : {'info': {'uuid': '5a920209-4855-4099-8b66-fb2a8d119759', 'side': 'ask', 'ord_type': 'limit', 'price': '4000000.0', 'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2019-02-09T10:12:50+09:00', 'volume': '0.0003', 'remaining_volume': '0.0003', 'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '0.0', 'locked': '0.0003', 'executed_volume': '0.0', 'trades_count': 0}, 'id': '5a920209-4855-4099-8b66-fb2a8d119759', 'timestamp': 1549674770000, 'datetime': '2019-02-09T01:12:50.000Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/KRW', 'type': 'limit', 'side': 'sell', 'price': 4000000.0, 'cost': 0.0, 'average': 4000000.0, 'amount': 0.0003, 'filled': 0.0, 'remaining': 0.0003, 'status': 'open', 'fee': {'currency': 'KRW', 'cost': 0.0}, 'trades': None}
            """
        except Exception as exp:
            print(exp)
    
    def _test_bithumb_buy(self):
        bithumb = self.get_bithumb()
        pass
        
    # def test_callPrivAPI(self):
    #     self.assertIsNotNone(self.bithumb.get_trading_fee())

    # def test_getBalance(self):
    #     balance = self.bithumb.get_balance('ETH')
    #     #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
    #     print(balance)
    
    # def test_buyError(self):
    #     coinName = 'BTC'
    #     usageKRW = 1000
    #     marketPrice = self.bithumb.get_current_price(coinName)
    #     marketPrice = (int)(marketPrice / 300)  #BTC의 경우 주문을 1000단위로 넣어야한다. 즉 이 오더는 수행되지 않는다.
    #     marketPrice = marketPrice * 1000
    #     orderCnt = usageKRW / marketPrice
        
    #     try:
    #         desc = self.bithumb.buy_limit_order(coinName, marketPrice, orderCnt)
    #         print(desc)
    #     except Exception as exp:
    #         print(exp)

    # def test_parsingResult(self):
    #     msg = {'status': '0000', 'order_id': '1548078639677728', 'data': [{'cont_id': '32762404', 'units': '0.0025', 'price': 3980000, 'total': 9950, 'fee': '14.93'}]}
    #     print(msg['data'][0]['fee'])
        

if __name__ == '__main__':
    unittest.main()


# print(hitbtc.fetch_order_book(hitbtc.symbols[0]))
# print(bitmex.fetch_ticker('BTC/USD'))
# print(huobi.fetch_trades('LTC/CNY'))

# print(exmo.fetch_balance())

# # sell one ฿ for market price and receive $ right now
# print(exmo.id, exmo.create_market_sell_order('BTC/USD', 1))

# # limit buy BTC/EUR, you pay €2500 and receive ฿1  when the order is closed
# print(exmo.id, exmo.create_limit_buy_order('BTC/EUR', 1, 2500.00))

# # pass/redefine custom exchange-specific order params: type, amount, price, flags, etc...
# kraken.create_market_buy_order('BTC/USD', 1, {'trading_agreement': 'agree'})
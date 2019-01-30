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
        apiKey = keys['api_key']
        apiSecret = keys['api_secret']
        
        bithumb = ccxt.bithumb({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        })
        
        # print(bithumb.fetch_balance())
        
    def test_upbit_pri_api(self):
        keys = util.readKey('./configs/upbit.key')
        apiKey = keys['key']
        apiSecret = keys['secret']
        
        upbit = ccxt.upbit({
                        'apiKey': apiKey,
                        'secret': apiSecret,
                        })
        
        print(upbit.fetch_balance())
        
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

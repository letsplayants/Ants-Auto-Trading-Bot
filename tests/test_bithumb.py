# -*- coding: utf-8 -*-
#!/usr/bin/env python
import unittest
import context
import sys
import os
import pkgutil
import prj_path

from utils import readKey
from pybithumb.client import Bithumb

class BithumbTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        keys = readKey('./configs/bithumb.key')
        self.apiKey = keys['api_key']
        self.apiSecret = keys['api_secret']

    def setUp(self):
        self.bithumb = Bithumb(self.apiKey, self.apiSecret)

    def tearDown(self):
        pass
    
    def test_callPubAPI(self):
        ret = Bithumb.get_tickers()
        self.assertIn('BTC', ret)
        
    def test_callPrivAPI(self):
        self.assertIsNotNone(self.bithumb.get_trading_fee())

    def test_getBalance(self):
        balance = self.bithumb.get_balance('ETH')
        #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
        print(balance)
    
    def test_buyError(self):
        coinName = 'BTC'
        usageKRW = 1000
        marketPrice = self.bithumb.get_current_price(coinName)
        marketPrice = (int)(marketPrice / 300)  #BTC의 경우 주문을 1000단위로 넣어야한다. 즉 이 오더는 수행되지 않는다.
        marketPrice = marketPrice * 1000
        orderCnt = usageKRW / marketPrice
        
        try:
            desc = self.bithumb.buy_limit_order(coinName, marketPrice, orderCnt)
            print(desc)
        except Exception as exp:
            print(exp)

    def test_parsingResult(self):
        msg = {'status': '0000', 'order_id': '1548078639677728', 'data': [{'cont_id': '32762404', 'units': '0.0025', 'price': 3980000, 'total': 9950, 'fee': '14.93'}]}
        print(msg['data'][0]['fee'])
        

if __name__ == '__main__':
    unittest.main()

# #============================================================================
# from pybithumb import Bithumb

# #제공하는 암호화폐 목록
# # print(Bithumb.get_tickers())

# #최근 체결가격
# # for coin in Bithumb.get_tickers():
# #     print(coin, Bithumb.get_current_price(coin))


# bithumb = Bithumb(api_key, api_secret)

# #수수료 조회
# # print(bithumb.get_trading_fee())

# #잔고 조회, 1초에 10회 이상 요청하면 API가 5분간 막힌다.. 아래의 코드는 10회 이상 요구하므로 5분간 무조건 막힘
# for coin in ['BTC', 'XRP', 'ETH']:
#     print(coin, bithumb.get_balance(coin))
    
# #매수 주문
# # desc = bithumb.buy_limit_order("ETH", 30000, 1)
# # print('buy order :{}'.format(desc))

# # #잔량 확인
# # quanity = bithumb.get_outstanding_order(desc)
# # print('buy quanity: {}'.format(quanity))

# # #주문 취소
# # status = bithumb.cancel_order(desc)
# # print('request cancel order: {}'.format(status))

# # try :
# # 	#매도 주문
# # 	desc = bithumb.sell_limit_order("ETH", 270000, 1)
# # 	print('sell order :{}'.format(desc))
	
# # 	quanity = bithumb.get_outstanding_order(desc)
# # 	print('sell quanity: {}'.format(quanity))
	
# # 	status = bithumb.cancel_order(desc)
# # 	print('request cancel order: {}'.format(status))
# # except Exception as exp:
# # 	print(exp)
		
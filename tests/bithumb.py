# -*- coding: utf-8 -*-
#!/usr/bin/env python
import unittest
import context
import sys
import os

from ants.exchanges import bithumb_client
from ants.read_api_key import readKey
from pybithumb import Bithumb

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
        self.assertIn(ret, 'BTCX')
        
    def test_callPrivAPI(self):
        self.assertTrue(False, 'Test Failed1')
        # self.assertTrue(True, 'Test Failed2')
        
        print(self.bithumb.get_trading_fee())
        
if __name__ == '__main__':
    unittest.main()



# api = XCoinAPI(api_key, api_secret);

# rgParams = {
# 	"order_currency" : "BTC",
# 	"payment_currency" : "KRW"
# };


# #
# # public api
# #
# # /public/ticker
# # /public/recent_ticker
# # /public/orderbook
# # /public/recent_transactions

# # result = api.xcoinApiCall("/public/ticker", rgParams);
# # print("status: " + result["status"]);
# # print("last: " + result["data"]["closing_price"]);
# # print("sell: " + result["data"]["sell_price"]);
# # print("buy: " + result["data"]["buy_price"]);


# #
# # private api
# #
# # endpoint		=> parameters
# # /info/current
# # /info/account
# # /info/balance
# # /info/wallet_address

# # result = api.xcoinApiCall("/info/account", rgParams);
# # print("status: " + result["status"]);
# # print("created: " + result["data"]["created"]);
# # print("account id: " + result["data"]["account_id"]);
# # print("trade fee: " + result["data"]["trade_fee"]);
# # print("balance: " + result["data"]["balance"]);


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
		
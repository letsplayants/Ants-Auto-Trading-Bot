# -*- coding: utf-8 -*- 
#!/usr/bin/env python

# Bithum API키를 사용하여 매수/매도를 기능을 호출한다
# 각종 설정 파일은 외부 TXT를 사용하여 읽어오도록 한다
# 모든 외부 기능은 로깅한다

# 로컬 web을 구동시켜 매매기록을 살핀다
# 로컬 web을 구동시켜 API Key를 저장하도록 한다


import sys
from bithumb_client import *
import pprint
from read_api_key import readKey

keys = readKey('bithumb.key')
api_key = keys[0]
api_secret = keys[1]

api = XCoinAPI(api_key, api_secret);

rgParams = {
	"order_currency" : "BTC",
	"payment_currency" : "KRW"
};


#
# public api
#
# /public/ticker
# /public/recent_ticker
# /public/orderbook
# /public/recent_transactions

result = api.xcoinApiCall("/public/ticker", rgParams);
print("status: " + result["status"]);
print("last: " + result["data"]["closing_price"]);
print("sell: " + result["data"]["sell_price"]);
print("buy: " + result["data"]["buy_price"]);


#
# private api
#
# endpoint		=> parameters
# /info/current
# /info/account
# /info/balance
# /info/wallet_address

result = api.xcoinApiCall("/info/account", rgParams);
print("status: " + result["status"]);
print("created: " + result["data"]["created"]);
print("account id: " + result["data"]["account_id"]);
print("trade fee: " + result["data"]["trade_fee"]);
print("balance: " + result["data"]["balance"]);



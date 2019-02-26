# -*- coding: utf-8 -*-
import logging
import time
import json
from datetime import datetime
import websocket
import threading
import ccxt
import decimal

from exchangem.model.exchange import Base
from exchangem.model.balance import Balance

class Bithumb(Base):
    def __init__(self, args={}):
        Base.__init__(self, args)

    def update(self, args):
        #빗썸은 소켓 방식을 지원하지 않으므로 옵져버 패턴을 사용하지 않는다
        pass
    
    def get_balance(self, target):
        #빗썸
        balance = Balance()
        ret = self.exchange.fetch_balance()
        if(not ret.get(target)):
            return None
            
        balance.add(target, ret[target]['total'], 
                            ret[target]['used'], 
                            ret[target]['free'])

        return balance
    
    def get_all_balance(self):
        #업비트는 전체 계좌 조회만 제공한다
        #빗썸은 어떨까~ ccxt에서 어디까지 지원할지 궁금
        balance = Balance()
        ret = self.exchange.fetch_balance()
        
        data = ret['info']['data']
        balance.add('KRW', 
                data['total_krw'],
                data['in_use_krw'],
                data['available_krw'])
                
        for symbol in self.exchange.symbols:
            name = symbol.split('/')[0].lower()
            try:
                balance.add(name.upper(),
                            data['total_' + name],
                            data['in_use_' + name],
                            data['available_' + name])
            except Exception as e:
                pass

        return balance
    
    def check_amount(self, symbol, seed, price):
        """
        코인 이름과 시드 크기를 입력받아서 매매 가능한 값을 돌려준다
        이때 수수료 계산도 함께 해준다
        매매가능한 크기가 거래소에서 지정한 조건에 부합하는지도 함께 계산해서
        돌려준다
        
        가령 주문 단위가 10으로 나눠서 떨어져야 한다면 계산값이 11이 나올경우
        10으로 돌려준다
        주문 가격이 오류인 경우 price오류와 함께 예외를 발생시킨다
        
        return 매매가능한 양, 가격, 수수료
        """
        #TODO KRW일 때는 확인했는데.. USDT, BTC, ETH일 때 확인을 안했음..
        
        
        #가격에 따라 주문할 수 있는 범위가 달라진다
        #이에 맞춰 주문할 수 있는 범위를 조정해준다
        # https://apidocs.bithumb.com/docs/marketBuy
        
        #빗썸 기준에 맞춰서 재작성 필요
        #빗썸은 주문의 합이 1000원 이상이면 주문이 된다고 나온다
        
        if(price > 2000000):
            div = 1000
        elif(price > 1000000):
            div = 500
        elif(price > 500000):
            div = 100
        elif(price > 100000):
            div = 50
        elif(price > 10000):
            div = 10
        elif(price > 1000):
            div = 5
        elif(price > 100):
            div = 1
        elif(price > 10):
            div = 0.1
        elif(price > 0):
            div = 0.01
        
        price -= price % div
        
        fee = self.get_fee(symbol.split('/')[1])
        fee_p = (seed / price) * fee
        seed -= fee_p
        amount = seed / price
        
        #빗썸은 100원 이하의 경우에만 소숫점 둘째 자리까지만 지원한다
        if(price >= 100):
            price = int(price)
        else:
            price = float("{:.2f}".format(price))
            
        coin_name = symbol.split('/')[0]
        if(coin_name == 'BTC'):
            amount = decimal.Decimal(amount).quantize(decimal.Decimal('.001'), rounding=decimal.ROUND_DOWN)
        else:
            amount = float("{:.4f}".format(amount))

        seed = float("{:.8f}".format(seed))
        fee_p = float("{:.8f}".format(fee_p))

        return amount, price, fee_p
        pass

    def get_last_price(self, symbol):
        ticker = self.exchange.fetch_ticker(symbol)
        self.logger.debug(ticker)
        """
        {'symbol': 'BTC/KRW', 'timestamp': 1549698009141, 'datetime': '2019-02-09T07:40:09.141Z', 'high': 4100000.0, 'low': 3776000.0, 'bid': 4002000.0, 'bidVolume': None, 'ask': 4004000.0, 'askVolume': None, 'vwap': 3927711.3257, 'open': 3778000.0, 'close': 4004000.0, 'last': 4004000.0, 'previousClose': None, 'change': 226000.0, 'percentage': 5.9820010587612495, 'average': 3891000.0, 'baseVolume': 5113.40675249, 'quoteVolume': 20083985614.66583, 'info': {'opening_price': '3778000', 'closing_price': '4004000', 'min_price': '3776000', 'max_price': '4100000', 'average_price': '3927711.3257', 'units_traded': '5113.40675249', 'volume_1day': '5113.40675249', 'volume_7day': '17281.38692642', 'buy_price': '4002000', 'sell_price': '4004000', '24H_fluctate': '226000', '24H_fluctate_rate': '5.98', 'date': '1549698009141'}}
        """
        return ticker['last']
        pass
    
    def get_fee(self, market):
        #빗썸의 경우 수수료 쿠폰을 사용하면 fee가 달라진다.
        #그러므로 account나 서버측에서 fee데이터를 읽어와야한다
        fee = 0.0015
            
        return fee
        
        
    def create_order(self, symbol, type, side, amount, price, params):
        #빗썸은 100원 이하의 경우에만 소숫점 둘째 자리까지만 지원한다
        price = decimal.Decimal(price).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
        if(price >= 100):
            price = int(price)
            
        amount = decimal.Decimal(amount).quantize(decimal.Decimal('.0001'), rounding=decimal.ROUND_DOWN)

        return super().create_order(symbol, type, side, amount, price, params)
        
if __name__ == '__main__':
    print('test')
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("__main__").setLevel(logging.DEBUG)
    # logging.getLogger("ccxt").setLevel(logging.WARNING)
    # logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    
    ex = Bithumb({'private_key_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/bithumb.conf'})

    print(Bithumb.mro())
    bal = ex.get_balance('없는코인')
    if(bal is not None):
        print(bal.get_all())
    
    bal = ex.get_balance('KRW')
    if(bal is not None):
        print(bal.get_all())
        print(bal.get('KRW'))
        
    print('balance---------------------------------------------------------------')
    print(ex.get_all_balance().get('KRW'))
    print(ex.get_all_balance().get_all())
    print('balance---------------------------------------------------------------')
    
    print('last price : ', ex.get_last_price('BTC/KRW'))
    print('fee : ', ex.get_fee('KRW'))
    amount, price, fee = ex.check_amount('BTC/KRW', 10000, 3900901)
    print('order : ', amount, price, fee)
    print('order : ', ex.check_amount('BTC/KRW', 10000, 0.9157))
    print('order : ', ex.check_amount('BTC/KRW', 10000, 12.9157))
    print('order : ', ex.check_amount('BTC/KRW', 10000, 163.9157))
    print('order : ', ex.check_amount('BTC/KRW', 10000, 8823.9157))
    print('order : ', ex.check_amount('BTC/KRW', 0.005, 4000000))
    
    print('KRW seed limit : ', ex.get_availabel_size('KRW'))
    print('BTC seed limit : ', ex.get_availabel_size('BTC'))
    print('ETH seed limit : ', ex.get_availabel_size('ETH'))
    print('EOS seed limit : ', ex.get_availabel_size('EOS'))
    print('seed limit : ', ex.get_availabel_size('EOS111'))
    
    print('has_market :', ex.has_market('BTC/KRW'))
    print('has_market :', ex.has_market('BTC/NONE'))
    
    
    # up.connect()
    
    
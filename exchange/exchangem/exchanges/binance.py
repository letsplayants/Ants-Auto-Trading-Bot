# -*- coding: utf-8 -*-
import logging
import time
import json
from datetime import datetime
import websocket
import threading
import ccxt
from ccxt.base.decimal_to_precision import decimal_to_precision  # noqa F401
from ccxt.base.decimal_to_precision import TRUNCATE              # noqa F401
from ccxt.base.decimal_to_precision import DECIMAL_PLACES        # noqa F401

from exchangem.model.exchange import Base
from exchangem.model.balance import Balance

class Binance(Base):
    def __init__(self, args={}):
        Base.__init__(self, args)
        
    def update(self, args):
        #TODO 소켓방식을 위하여 남겨둔다
        pass
    
    def get_balance(self, target):
        balance = Balance()
        ret = self.exchange.fetch_balance()
        if(not ret.get(target)):
            return None
            
        balance.add(target, ret[target]['total'],
                            ret[target]['used'], 
                            ret[target]['free'])

        return balance
    
    def get_all_balance(self):
        balance = Balance()
        ret = self.exchange.fetch_balance()
        
        for item in ret['info']['balances']:
            name = item['asset']
            total = item['free'] + item['locked']
            try:
                balance.add(name.upper(),
                            total,
                            item['locked'],
                            item['free'])
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
        #BNB를 사용하여 수수료를 지불할 경우 seed만큼 amount를 매매할 수 있다.
        #BNB를 사용하지 않을 경우 fee를 계산하도록 해야한다.
        #만약 BNB가 지불해야할 수수료만큼 되지 않는다면... BNB를 차감하고 모자란 금액에 해당하는 fee를 계산해야한다
        #본 프로그램에서는 BNB와 상관없이 그냥 fee를 계산하여 그 금액만큼 덜 매매하는 것으로 처리한다
        
        #Binance Filter
        #https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#filters
        # 심볼을 사용하여 exchangeinfo를 얻은 후 각각의 정보를 대입하여 입력값 제한을 한다
        # {'symbol': 'ETHBTC', 'status': 'TRADING', 'baseAsset': 'ETH', 'baseAssetPrecision': 8, 'quoteAsset': 'BTC', 'quotePrecision': 8, 'orderTypes': ['LIMIT', 'LIMIT_MAKER', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'], 'icebergAllowed': True, 'filters': [{'filterType': 'PRICE_FILTER', 'minPrice': '0.00000000', 'maxPrice': '0.00000000', 'tickSize': '0.00000100'}, {'filterType': 'PERCENT_PRICE', 'multiplierUp': '10', 'multiplierDown': '0.1', 'avgPriceMins': 5}, {'filterType': 'LOT_SIZE', 'minQty': '0.00100000', 'maxQty': '100000.00000000', 'stepSize': '0.00100000'}, {'filterType': 'MIN_NOTIONAL', 'minNotional': '0.00100000', 'applyToMarket': True, 'avgPriceMins': 5}, {'filterType': 'ICEBERG_PARTS', 'limit': 10}, {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}]}
        
        seed = float(seed)
        price = float(price)
        
        fee = float(decimal_to_precision(self.get_fee_symbol(symbol), TRUNCATE, 8, DECIMAL_PLACES))
        fee_p = (seed / price) * fee
        amount = (seed / price) - fee_p
        
        markets = self.markets.get(symbol)
        if(markets == None):
            return 0, 0, 0
        
        filters = markets['info']['filters']
        
        #min의 경우는 오더에서 오류가 발생하므로 문제없음
        #max의 경우는 자금력의 부족으로 발생하기 힘들듯..
        for filter in filters:
            if(filter == 'PRICE_FILTER'): #price
                minPrice = filter['minPrice']
                maxPrice = filter['maxPrice']
                tickSize = filter.get('tickSize')   #변화되는 최소 값
                price = price % tickSize
            elif (filter == 'LOT_SIZE'): #amount
                minQty = filter['minQty']
                maxQty = filter['maxQty']
                stepSize = filter.get('stepSize')
                amount = amount % stepSize
        
        amount = decimal_to_precision(amount, TRUNCATE, 8, DECIMAL_PLACES)
        price = decimal_to_precision(price, TRUNCATE, 8, DECIMAL_PLACES)
        seed = decimal_to_precision(seed, TRUNCATE, 8, DECIMAL_PLACES)
        fee_p = decimal_to_precision(fee_p, TRUNCATE, 8, DECIMAL_PLACES)

        return amount, price, fee_p
        pass

    def get_last_price(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
        except Exception as exp:
            #TODO 거래소 예외로 교체한다
            print(exp)
            return None
            
        self.logger.debug(ticker)
        """
        {'symbol': 'BTC/KRW', 'timestamp': 1549698009141, 'datetime': '2019-02-09T07:40:09.141Z', 'high': 4100000.0, 'low': 3776000.0, 'bid': 4002000.0, 'bidVolume': None, 'ask': 4004000.0, 'askVolume': None, 'vwap': 3927711.3257, 'open': 3778000.0, 'close': 4004000.0, 'last': 4004000.0, 'previousClose': None, 'change': 226000.0, 'percentage': 5.9820010587612495, 'average': 3891000.0, 'baseVolume': 5113.40675249, 'quoteVolume': 20083985614.66583, 'info': {'opening_price': '3778000', 'closing_price': '4004000', 'min_price': '3776000', 'max_price': '4100000', 'average_price': '3927711.3257', 'units_traded': '5113.40675249', 'volume_1day': '5113.40675249', 'volume_7day': '17281.38692642', 'buy_price': '4002000', 'sell_price': '4004000', '24H_fluctate': '226000', '24H_fluctate_rate': '5.98', 'date': '1549698009141'}}
        """
        return ticker['last']
        pass
    
    def get_fee_symbol(self, symbol, taker=True):
        str = 'taker'
        if(not taker):
            str = 'maker'
            
        return self.markets.get(symbol).get(str)
    
    def get_fee(self, market):
        """
        심볼을 사용하여 심볼별 수수료를 얻어올 수도 있다.
        print self.markets['BTC/USDS']
        
        {'fee_loaded': False, 'percentage': True, 'tierBased': False, 'taker': 0.001, 'maker': 0.001, 'precision': {'base': 8, 'quote': 8, 'amount': 6, 'price': 2}, 'limits': {'amount': {'min': 1e-06, 'max': 10000000.0}, 'price': {'min': None, 'max': None}, 'cost': {'min': 10.0, 'max': None}}, 'id': 'BTCUSDS', 'symbol': 'BTC/USDS', 'base': 'BTC', 'quote': 'USD
        
        # https://www.binance.com/en/fee/schedule
        바낸은 티어 베이스로 수수료를 측정한다.
        가장 낮은 티어의 수수료는 0.001이다. 여기서는 그냥 최저 티어의 수수료로 계산한다
        """
        fee = 0.001
        
        return fee
        
        
    # def create_order(self, symbol, type, side, amount, price, params):
    #     #빗썸은 100원 이하의 경우에만 소숫점 둘째 자리까지만 지원한다
    #     if(price >= 100):
    #         price = int(price)
    #     else:
    #         price = float("{:.2f}".format(price))
            
    #     amount = decimal.Decimal(amount).quantize(decimal.Decimal('.0001'), rounding=decimal.ROUND_DOWN)

    #     desc = self.exchange.create_order(symbol, type, side, amount, price, params)
    #     return desc
    
        
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
    
    ex = Binance({'root_config_file':'configs/ants.conf', 'key_file':'configs/exchanges.key', 'config_file':'configs/binance.conf'})

    print(Binance.mro())
    bal = ex.get_balance('없는코인')
    if(bal is not None):
        print(bal.get_all())
    
    bal = ex.get_balance('TRX')
    if(bal is not None):
        print(bal.get('TRX'))
        
    print('balance---------------------------------------------------------------')
    print(ex.get_all_balance().get('BTC'))
    print('balance---------------------------------------------------------------')
    
    print('last price : ', ex.get_last_price('TRX/BTC'))
    print('last price : ', ex.get_last_price('BTC/USDT'))
    print('fee : ', ex.get_fee('USDT'))
    print('order : ', ex.check_amount('TRX/BTC', 10000, 0.9157))
    print('order : ', ex.check_amount('BTC/USDT', 10000, 12.9157))
    print('order : ', ex.check_amount('BTC/USDT', 10000, 163.9157))
    print('order : ', ex.check_amount('BTC/USDT', 10000, 8823.9157))
    print('order : ', ex.check_amount('BTC/USDT', 0.005, 4000000))
    
    print('USDT seed limit : ', ex.get_availabel_size('USDT'))
    print('BTC seed limit : ', ex.get_availabel_size('BTC'))
    print('ETH seed limit : ', ex.get_availabel_size('ETH'))
    print('BNB seed limit : ', ex.get_availabel_size('BNB'))
    print('TRX seed limit : ', ex.get_availabel_size('TRX'))
    print('DENT seed limit : ', ex.get_availabel_size('DENT'))
    print('seed limit : ', ex.get_availabel_size('EOS111'))
    
    print('has_market :', ex.has_market('BTC/USDT'))
    print('has_market :', ex.has_market('BTC/NONE'))
    
    print('fee :', ex.get_fee_symbol('BTC/USDT', False))
    
    
    
    # up.connect()
    
    
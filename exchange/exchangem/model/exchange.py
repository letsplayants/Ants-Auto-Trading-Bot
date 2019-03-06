# -*- coding: utf-8 -*-

"""
거래소
- 공통 기능
- 필수 기능 목록을 넣어둔다.
"""

import abc
import decimal
import binascii
import logging
import ccxt
import base64
import requests
from datetime import datetime

from ccxt.base.decimal_to_precision import decimal_to_precision  # noqa F401
from ccxt.base.decimal_to_precision import TRUNCATE              # noqa F401
from ccxt.base.decimal_to_precision import ROUND                 # noqa F401
from ccxt.base.decimal_to_precision import DECIMAL_PLACES        # noqa F401
from ccxt.base.decimal_to_precision import SIGNIFICANT_DIGITS    # noqa F401
from ccxt.base.decimal_to_precision import PAD_WITH_ZERO         # noqa F401
from ccxt.base.decimal_to_precision import NO_PADDING            # noqa F401

from exchangem.model.observers import ObserverNotifier
from exchangem.crypto import Crypto
from exchangem.utils import Util as util
from exchangem.model.trading import Trading

class Base(ObserverNotifier, metaclass=abc.ABCMeta):
    def __init__(self, args={}):
        ObserverNotifier.__init__(self)
        orderes = []
        self.exchange = None
        self.config = {}
        self.telegram = args.get('telegram')
        self.is_debug_mode = False
        
        #exchange가 생성될 때 마다 sqlite가 생성된다.
        #session이 race condition에 걸릴 수 있다. 
        #구조를 고쳐야함
        self.db = args.get('db')
        
        self.logger = logging.getLogger(__name__)
        
        exchange_obj = None
        for id in ccxt.exchanges:
            if(id == self.__class__.__name__.lower()):
                exchange_obj = getattr(ccxt, id)
                break
            
        try:
            self.logger.debug(args)
            key_set = self.load_key(args['root_config_file'], args['key_file'], self.__class__.__name__)
            self.exchange = exchange_obj(key_set)
        except :
            self.exchange = exchange_obj()
            self.logger.warning('Key file loading failed.')
        
        self.markets = self.exchange.loadMarkets()
        self.save_key_market_price()
        
        if(args.get('config_file')):
            self.logger.info('config file file : {}'.format(args.get('config_file')))
            self.config = self.load_config(args.get('config_file'))
            
        if(args.get('root_config_file')):
            try:
                self.is_debug_mode = self.load_config(args.get('root_config_file')).get('test_mode')
                if(self.is_debug_mode.upper() == 'TRUE'):
                    self.logger.info('EXCHANGE RUN IN DEBUG MODE. WILL NOT DO BUY/SELL')
                    self.is_debug_mode = True
                else:
                    self.is_debug_mode = False
            except:
                self.is_debug_mode = False
            
    pass

    def load_key(self, private_key_file, encrypted_file, exchange_name):
        crypto = Crypto()
        crypto.readKey(private_key_file)
        exchanges = crypto.read_encrytion_file(encrypted_file)
        
        en_key_set = exchanges[exchange_name.lower()]
        
        data = en_key_set['apiKey']
        borg = binascii.a2b_base64(data)
        apiKey = crypto.decrypt(borg)
        
        data = en_key_set['secret']
        borg = binascii.a2b_base64(data)
        secret = crypto.decrypt(borg)
        
        key_set = {
            'apiKey': apiKey,
            'secret': secret
        }
        return key_set
    
    def load_config(self, file_name):
        return util.readConfig(file_name)
        
    @abc.abstractmethod
    def get_balance(self, target):
        pass
    
    def create_order(self, symbol, type, side, amount, price, params):
        if(self.is_debug_mode == True):
            self.logger.info('EXCHANGE IN TEST MODE : {} {} {} {} {}'.format(symbol, type, side, amount, price))
            return {'TEST_MODE':'True'}
                
        try:    
            desc = self.exchange.create_order(symbol, type, side, amount, price, params)
        except Exception as exp:
            raise exp
        
        try:
            #DB에 기록
            coin_name = symbol.split('/')[0]
            market = symbol.split('/')[1]
            # type = type
            # side = 'buy'
            # amount = 1.1
            # price = 0.45
            params = str(params)
            time = datetime.now()
            request_id = str(desc)
            exchange_name = self.__class__.__name__.lower()
            
            record = Trading(
                         coin_name,
                         market,
                         type,
                         side,
                         amount,
                         price,
                         params,
                         time,
                         request_id,
                         exchange_name)
            
            total = self.decimal_to_precision(float(amount) * float(price))
                
            self.telegram.send_message('오더를 냄 : {}, {}, {}/{}, 주문 개수:{}, 주문단가:{}, 총 주문금액:{}'.format(
                                        exchange_name.upper(), 
                                        side.upper(),
                                        coin_name.upper(), 
                                        market.upper(), 
                                        amount, 
                                        price, 
                                        total) )
            self.db.add(record)
            
            
        except Exception as exp:
            raise exp
            
        return desc

    @abc.abstractmethod
    def check_amount(self, coin_name, seed_size, price):
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
        pass

    @abc.abstractmethod
    def get_last_price(self, symbol):
        pass
    
    @abc.abstractmethod
    def get_fee(self, market):
        pass
    
    def get_availabel_size(self, coin_name):
        """
        coin_name의 사용 제한 값을 돌려준다
        법정화폐 및 통화도 코인으로 간주하여 처리한다
        freeze_size : 사용하지 않고 남겨둘 자산의 크기
        availabel_size : 사용할 자산의 크기
        """
        coin_name = coin_name.upper()

        freeze_conf = self.config.get('freeze_size')
        if(freeze_conf == None):
            freeze_size = 0
        else:
            freeze_size = freeze_conf.get(coin_name)
            if(freeze_size == None):
                freeze_size = 0

        availabel_conf = self.config.get('availabel_size')
        if(availabel_conf != None):
            coin_size = availabel_conf.get(coin_name)
            if(coin_size != None):
                coin_size = coin_size - freeze_size
                if(coin_size < 0):
                    coin_size = 0
            else :
                coin_size = None    #설정값이 없음
        self.logger.debug('get_availabel_size name : {}, freeze_size: {}, availabel_size: {}'.format(coin_name, freeze_size, coin_size))

        balance = self.get_balance(coin_name)
        if(balance == None or balance.get(coin_name) == None):
            #해당 코인의 잔고가 0일 경우
            self.logger.debug('get_availabel_size balance : {}'.format(balance))
            return 0
        
        if(coin_size == None):
            #None이란 의미는 설정값이 없다는 의미
            #설정값이 없으면 잔고에 남아있는 모든 금액을 사용할 수 있으므로 
            #0으로 설정해 거래를 막아버린다
            # ret = balance.get(coin_name)['free']
            ret = 0
            ret = self.decimal_to_precision(ret)
            self.logger.debug('get_availabel_size availabel_size is not setting : {}'.format(coin_size))
            return ret

        
        if(coin_size < balance.get(coin_name)['free']):
            return coin_size
        else:
            ret = balance.get(coin_name)['free']
            ret = self.decimal_to_precision(ret)
            return ret

    
    def has_market(self, market):
        try:
            r = self.exchange.markets[market]
        except Exception as exp:
            self.logger.warning(exp)
            r = None
            
        if(r != None):
            return True
        else:
            return False
        
    def decimal_to_precision(self, value):
        return float(decimal_to_precision(value, TRUNCATE, 8, DECIMAL_PLACES))
        
    def except_parsing(self, exp):
        #ccxt에서 예외 args를 공백(' ')으로 구분해서 넣어줌.
        exp_str = exp.args[0]
        error = exp.args[0][exp_str.index(' '):]
        dd = eval(error)
        return dd.get('error').get('message')
        
    def get_BTC_price(self):
        #BTC / USDT의가격을 돌려준다.
        pass
    
    def get_key_market_price(self, key_coin):
        """
        기축 통화 가격을 USDT 기준으로 돌려준다.
        """
        symbol = key_coin + '/USDT'
        r = self.key_market_price.get(symbol)
        if(r == None):
            symbol = key_coin + '/KRW'
            r = self.key_market_price.get(symbol)
            if(r == None):
                raise Exception('{} is not key coin'.format(symbol))
                
            krw_rate = self.get_usd_krw()
            r = r / krw_rate
        
        return r
        
    def is_small_balance(self, count, market):
        BASE_PRICE_USDT = 0.5
        
        if(market == 'KRW'):
            if(count < BASE_PRICE_USDT * 1300):
                return True
            else:
                return False
        
        if(market == 'USDT'):
            if(count < BASE_PRICE_USDT):
                return True
            else:
                return False
        
        #KRW을 제외한 ETH, BTC일 경우
        pre_price = self.get_key_market_price(market)
        
        price = count * pre_price
        if(price < BASE_PRICE_USDT):
            return True
        else:
            return False
        
    def get_usd_krw(self):
        #업비트 환율 정보를 얻어온다
        url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        
        info = requests.get(url, headers=headers).json()
        return info[0]['basePrice']

    def save_key_market_price(self):
        #해당 거래소의 BTC가격을 저장하고 있는다.
        # 마켓 정보중 USDT가 있는지 확인 후 BTC 가격 저장
        # KRW마켓의 BTC가 있으면 환율 정보와 함께 나눈 후 BTC가격 저장
        # 이왕하는거 ETH나 다른 것들도 저장할까?...
        
        #key market list를 얻어온다.
        #USDT, ETH, BTC를 주요 key로 본다
        
        self.key_currency = ['BTC/KRW', 'BTC/USDT', 'ETH/KRW', 'ETH/USDT', 'BNB/USDT']
        self.key_market_price = {}
        self.logger.debug('-'*80)
        # print(self.exchange.markets.keys())
        for item in self.exchange.markets.keys():
            try:
                self.key_currency.index(item)
                self.key_market_price[item] = self.get_last_price(item)
            except Exception as exp:
                self.logger.debug('It is ok : {}'.format(exp))
                pass
                
        self.logger.debug('key market price : {}'.format(self.key_market_price))
        self.logger.debug('-'*80)
        
    
class SupportWebSocket(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def open(self):
        pass
    
    @abc.abstractmethod
    def close(self):
        pass
    
    @abc.abstractmethod
    def connect(self):
        pass
    

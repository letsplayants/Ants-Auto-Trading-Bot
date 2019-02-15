# -*- coding: utf-8 -*-

"""
거래소가 반드시 가져야하는 기능 목록을 넣어둔다.
"""

import abc
import decimal
import binascii
import logging
import ccxt

from ccxt.base.decimal_to_precision import decimal_to_precision  # noqa F401
from ccxt.base.decimal_to_precision import TRUNCATE              # noqa F401
from ccxt.base.decimal_to_precision import ROUND                 # noqa F401
from ccxt.base.decimal_to_precision import DECIMAL_PLACES        # noqa F401
from ccxt.base.decimal_to_precision import SIGNIFICANT_DIGITS    # noqa F401
from ccxt.base.decimal_to_precision import PAD_WITH_ZERO         # noqa F401
from ccxt.base.decimal_to_precision import NO_PADDING            # noqa F401

from exchangem.model.observers import ObserverNotifier
from exchangem.crypto import Crypto
from exchangem.utils import Util

class Base(ObserverNotifier, metaclass=abc.ABCMeta):
    def __init__(self, args={}):
        ObserverNotifier.__init__(self)
        orderes = []
        self.exchange = None
        self.config = {}
        
        self.logger = logging.getLogger(__name__)
        
        exchange_obj = None
        for id in ccxt.exchanges:
            if(id == self.__class__.__name__.lower()):
                exchange_obj = getattr(ccxt, id)
                break
            
        try:
            key_set = self.load_key(args['private_key_file'], args['key_file'], self.__class__.__name__)
            self.exchange = exchange_obj(key_set)
        except :
            self.exchange = exchange_obj()
            self.logger.warning('Key file loading failed.')
        
        self.markets = self.exchange.loadMarkets()

        if(args.get('config_file')):
            self.logger.info('config file file : {}'.format(args.get('config_file')))
            self.config = self.load_config(args.get('config_file'))
    pass

    def load_key(self, private_key_file, encrypted_file, exchange_name):
        crypto = Crypto()
        crypto.readKey(private_key_file)
        exchanges = crypto.read_encrytion_file(encrypted_file)
        
        en_key_set = exchanges[exchange_name.upper()]
        
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
        return Util.readKey(file_name)
        
    @abc.abstractmethod
    def get_balance(self, target):
        pass
    
    def create_order(self, symbol, type, side, amount, price, params):
        desc = self.exchange.create_order(symbol, type, side, amount, price, params)
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
    def get_last_price(self, coin_name):
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

        balance = self.get_balance(coin_name)
        if(balance == None or balance.get(coin_name) == None):
            #해당 코인의 잔고가 0일 경우
            return 0
        
        if(coin_size == None):
            #None이란 의미는 설정값이 없다는 의미
            ret = balance.get(coin_name)['free']
            ret = decimal_to_precision(ret, TRUNCATE, 8, DECIMAL_PLACES)
            return ret

        
        if(coin_size < balance.get(coin_name)['free']):
            return coin_size
        else:
            ret = balance.get(coin_name)['free']
            ret = decimal_to_precision(ret, TRUNCATE, 8, DECIMAL_PLACES)
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
        return decimal_to_precision(value, TRUNCATE, 8, DECIMAL_PLACES)
        
    def except_parsing(self, exp):
        #ccxt에서 예외 args를 공백(' ')으로 구분해서 넣어줌.
        exp_str = exp.args[0]
        error = exp.args[0][exp_str.index(' '):]
        dd = eval(error)
        return dd.get('error').get('message')
    
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
    

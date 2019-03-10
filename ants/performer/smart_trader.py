# -*- coding: utf-8 -*-
import logging

from exchangem.model.observers import Observer

class SmartTrader:
    """
    config 
      - 트레이딩에 사용할 금액. 없으면 거래소에서 사용가능한 금액으로 사용한다
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchanges = {}
        pass
    
    def config(self):
        self.configs = {
            'upbit':{
                'krw_limit': 10000,
                'btc_limit': 1
            },
            'bithumb':{
                'krw_limit': 10000
            },
            'binance':{
                'btc_limit': 0.5,
                'usdt_limit': 10
            }
        }
        pass
    
    def add_exchange(self, name, exchange):
        self.exchanges[name] = exchange
    
    def trading(self, exchange_name, market, action, coin_name, price=None, amount=None):
        """
        사용가능한 금액에 맞춰서 개수를 구매한다
        """
        exchange = self.exchanges.get(exchange_name)
        if(exchange == None):
            self.logger.warning('{} is not support'.format(exchange))
            return None
        self.logger.debug('select exchange : {}'.format(exchange))
        
        symbol = coin_name + '/' + market #'BTC/KRW'
        if(not exchange.has_market(symbol)):
            self.logger.warning('{} has not market : {}'.format(exchange, market))
            return None

        self.logger.info('Try Action {} {}/{} {}'.format(exchange_name, coin_name, market, action))
        if(action == 'BUY'):
            seed_money = self.availabel_seed_money(exchange, market)
            ret = self._buy(exchange, market, coin_name, seed_money, price)
        elif(action == 'SELL'):
            ret = self._sell(exchange, market, coin_name, price, amount)
            
        if(ret is None):
            self.logger.warning('action fail')
            return None
        
        return ret

    def _buy(self, exchange, market, coin_name, seed_size, price):
        symbol = coin_name + '/' + market #'BTC/KRW'
        _type = 'limit'  # or 'market' or 'limit'
        side = 'buy'  # 'buy' or 'sell'
        amount = 0
        
        if(price == None):
            price = exchange.get_last_price(symbol)
        amount, price, fee = exchange.check_amount(symbol, seed_size, price)
        params = {}
        desc = None
        
        self.logger.info('_buy - price: {}, amount: {}, fee: {}'.format(price, amount, fee))
        try:
            desc = exchange.create_order(symbol, _type, side, amount, price, params)
            self.logger.debug('order complete : {}'.format(desc))
        except Exception as exp:
            self.logger.warning('create_order exception : {}'.format(exp))
            
        return desc
    
    def _sell(self, exchange, market, coin_name, price, amount):
        symbol = coin_name + '/' + market #'BTC/KRW'
        _type = 'limit'  # or 'market' or 'limit'
        side = 'sell'  # 'buy' or 'sell'
        
        if(price == None):
            price = exchange.get_last_price(symbol)
        
        if(amount == None):
            amount = exchange.get_availabel_size(coin_name)
        
        if(amount == 0):
            self.logger.warning('{} is not enought {}'.format(coin_name, amount))
        
        # amount, price, fee = exchange.check_amount(symbol, amount, price)
        fee_p = exchange.get_fee(market)
        fee = float(amount) * fee_p
        params = {}
        desc = None
        
        price = exchange.decimal_to_precision(price)
        amount = exchange.decimal_to_precision(amount)
        fee = exchange.decimal_to_precision(fee)
        self.logger.info('_sell - price: {}, amount: {}, fee: {}'.format(price, amount, fee))
        try:
            desc = exchange.create_order(symbol, _type, side, amount, price, params)
            self.logger.debug('order complete : {}'.format(desc))
        except Exception as exp:
            self.logger.warning('create_order exception : {}'.format(exp))
            
        return desc
        
    def availabel_seed_money(self, exchange, base):
        """
        사용 가능한 market base seed를 돌려준다
        1. config에서 설정된 값
        2. exchange별 설정된 값
        3. exchange에 가용 가능한 모든 머니
        """
        sm = exchange.get_availabel_size(base)
        self.logger.debug('{} seed_money : {}'.format(base, sm))
        return sm
    
    def trading_limit(self, exchange, action, count, price):
        """
        fee만 계산해서 지정된 가격에 맞게 매매한다
        """
        pass
    
    def get_balance(self, exchange_name, coin_name, market):
        """
        거래소 잔고를 가져온다. 
        이 때 small balance의 경우 0으로 처리한다
        """
        exchange = self.exchanges.get(exchange_name)
        symbol = coin_name + '/'+ market
        
        if(not exchange.has_market(symbol)):
            raise Exception('{} is not support in {}'.format(symbol, exchange_name))
        
        bal = exchange.get_balance(coin_name)
        if(bal is None):
            return 0
            
        
        target_price = exchange.get_last_price(symbol)
        print(bal.get(coin_name))
        
        target_cnt = bal.get(coin_name)['free']
        t_price = target_price * target_cnt
        
        if(exchange.is_small_balance(t_price, market) is True):
            return 0
        
        return target_cnt
        
        #KRW, USDT를 기축으로 계산해야함
        #프로그램의 계산 기축은 USDT로 측정 모든 기준은 USDT를 기준으로 계산함
        #달러로 1달러 미만은 스몰 밸런스로 판정한다
        #다만 화면에 표시할 때에는 KRW로 환산하여 계산할 수 있음
        #기축으로 BTC만 받도록한다. BTC이외는 구매할 수 없는 가격을 돌려준다.
        
        # Is it small balance?
    
if __name__ == '__main__':
    print('SmartTrader test')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    
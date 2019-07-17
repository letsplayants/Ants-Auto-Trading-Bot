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
    
    def add_exchange(self, name, exchange):
        self.exchanges[name] = exchange
        
    def get_order_detail(self, exchange, order_id):
        exchange = self.exchanges.get(exchange)
        return exchange.get_private_orders_detail(order_id)
        
    def get_private_orders(self, exchange):
        exchange = self.exchanges.get(exchange)
        return exchange.get_private_orders()
    
    def fetch_orders_by_uuids(self, exchange, uuids):
        if(uuids is None or len(uuids) == 0):
            return None
            
        exchange = self.exchanges.get(exchange)
        return exchange.fetch_orders_by_uuids(uuids)
    
    def trading(self, exchange_name, market, action, coin_name, price=None, amount=None, etc={}):
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

        action = action.upper()
        self.logger.info('Try Action {} {}/{} {}'.format(exchange_name, coin_name, market, action))
        if(action == 'BUY'):
            #TODO seed_money 체크하는 루틴은 왜 여기있는거지? _buy 함수에 포함되는게 맞지 않나???
            seed_money = self.availabel_seed_money(exchange, market)
            if(amount != None):
                # 여기서 amount는 시드 머니를 의미한다
                seed_money = self.check_percent(exchange, seed_money, amount)
                pass
                
            ret = self._buy(exchange, market, coin_name, seed_money, price, etc)
        elif(action == 'SELL'):
            ret = self._sell(exchange, market, coin_name, price, amount, etc)
        
        if(ret is None):
            self.logger.warning('action fail')
            return None
        
        return ret
    
    def check_percent(self, exchange, seed_money, req_sm):
        req_sm = str(req_sm)
        if(req_sm.count('%') != 0):
            percent = req_sm.split('%')[0]
            percent = int(percent)
            if(percent < 0):
                percent = 0
            if(percent > 100):
                percent = 100
                
            percent = percent / 100
            seed_money = seed_money * percent
            return exchange.decimal_to_precision(seed_money)
        else:
            req_sm = float(req_sm)
            if(seed_money > req_sm):
               seed_money = req_sm 
            return exchange.decimal_to_precision(float(seed_money))
    
    def _buy(self, exchange, market, coin_name, seed_size, price=None, etc={}):
        symbol = coin_name + '/' + market #'BTC/KRW'
        _type = 'limit'  # or 'market' or 'limit'
        side = 'buy'  # 'buy' or 'sell'
        amount = 0
        
        last_price = exchange.decimal_to_precision(exchange.get_last_price(symbol))
        
        if(price == None):
            price = str(last_price)
        
        price = str(price)
        if(price.count('%') != 0):
            percent = price.split('%')[0]
            percent = int(percent)
            percent = percent / 100
            price = last_price + (last_price * percent)
        else:
            price = float(price)
        
        price = exchange.decimal_to_precision(price)
        
        if(price >= last_price * 1.5):
            raise Exception('구매단가가 너무 높습니다.(현재가 1.5배 초과) 주문을 취소합니다.\n현재가:{}\n주문가:{}'.format(last_price, price))
        
        self.logger.debug('price: {}, last_price: {}'.format(price, last_price))
        
        
        amount, price, fee = exchange.check_amount(symbol, seed_size, price)
        params = {}
        desc = None
        
        self.logger.info('_buy - price: {}, amount: {}, fee: {}'.format(price, amount, fee))
        try:
            desc = exchange.create_order(symbol, _type, side, amount, price, params, etc)
            self.logger.debug('order complete : {}'.format(desc))
        except Exception as exp:
            self.logger.warning('create_order exception : {}'.format(exp))
            raise Exception('주문 중 오류가 발생하였습니다 : {}'.format(exp))
            
        return desc
    
    def _sell(self, exchange, market, coin_name, price=None, amount=None, etc={}):
        symbol = coin_name + '/' + market #'BTC/KRW'
        _type = 'limit'  # or 'market' or 'limit'
        side = 'sell'  # 'buy' or 'sell'
        
        #판매 단가가 너무 낮은지 체크
        last_price = exchange.decimal_to_precision(exchange.get_last_price(symbol))
        if(price == None):
            price = str(last_price)
        
        price = str(price)   
        
        if(price.count('%') != 0):
            percent = price.split('%')[0]
            percent = int(percent)
            percent = percent / 100
            price = last_price + (last_price * percent)
        else:
            price = float(price)
        
        price = exchange.decimal_to_precision(price)
        
        if(price <= last_price * 0.5):
            raise Exception('판매단가가 너무 낮습니다.(현재가의 절반 미만) 주문을 취소합니다.\n현재가:{}\n주문가:{}'.format(last_price, price))
        
        self.logger.debug('price: {}, last_price: {}'.format(price, last_price))
        
        
        if(price == None):
            price = exchange.get_last_price(symbol)
        
        free_amount = exchange.get_availabel_size(coin_name, False)
        if(amount == None):
            amount = free_amount
        
        amount = self.check_percent(exchange, free_amount, amount)
        self.logger.debug('amount: {}, free_amount: {}'.format(amount, free_amount))
        
        if(amount == 0):
            self.logger.warning('{} is not enought {}'.format(coin_name, amount))
            raise Exception('{} 여유가 충분하지 않습니다.\n잔고:{}'.format(coin_name, amount))
        
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
            desc = exchange.create_order(symbol, _type, side, amount, price, params, etc)
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
        #2019-06-03
        #cache가 도입되면서 사용가능한 금액 부분이 올바르게 안나올 수 있다.
        #100원에서 90원을 사용했는데 연속 주문이 들어올 경우 캐시된 100원이 그대로
        #사용 가능한 금액으로 나와서 문제가 될 수 있다
        #다만 이 경우 어떨 때는 금액이 자투리 금액을 다 사용하고 어떨 때는 
        #주문 자체가 안들어가는 경우이다.
        sm = exchange.get_availabel_size(base)
        self.logger.debug('{} seed_money : {}'.format(base, sm))
        return sm
    
    def trading_limit(self, exchange, action, count, price):
        """
        fee만 계산해서 지정된 가격에 맞게 매매한다
        """
        pass
    
    def get_balance(self, exchange_name, coin_name, market, only_free=True):
        """
        거래소 잔고를 가져온다. 
        이 때 small balance의 경우 0으로 처리한다
        잔고는 free와 used와 total로 구성된다. only_free가 아니면 total(free + used)값을 돌려준다.
        """
        exchange = self.exchanges.get(exchange_name)
        symbol = coin_name + '/'+ market
        
        if(not exchange.has_market(symbol)):
            raise Exception('{} is not support in {}'.format(symbol, exchange_name))
        
        bal = exchange.get_balance(coin_name)
        if(bal is None):
            return 0
        self.logger.debug('{} balance : {}'.format(symbol, bal.get(coin_name)))
        
        target_price = exchange.get_last_price(symbol)
        target_cnt = bal.get(coin_name)['free']
        if(not only_free):
            target_cnt += bal.get(coin_name)['used']
            
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
    
    def cancel_order(self, exchange_name, id):
        exchange = self.exchanges.get(exchange_name)
        return exchange.cancel_private_order(id)
        
    
if __name__ == '__main__':
    print('SmartTrader test')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    
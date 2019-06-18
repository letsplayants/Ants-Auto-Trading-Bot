# -*- coding: utf-8 -*-
import logging
import json

class BaseClass():
	pass

class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class PriceStorage(BaseClass, metaclass=Singleton):
    """
    모든 코인의 가격 정보를 메모리에 들고 관리한다
    
    {
        "KRW":
        {
            "BTC":{
                last_price:10000000.00
                timestamp:1234500000
            },
            "ETH":{
                last_price:10000000.00
                timestamp:1234500000
            }
        },
        "BTC":
        {
            "ETH":{
                last_price:0.0001
                timestamp:123456789
            }
        }
    }
    """
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.price = {}

    def __repr__(self):
        return str(dict(self))
        
    def __iter__(self):
        klass = self.__class__
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        iters.update(self.__dict__)

        include=['price']
        for x,y in iters.items():
            if(x in include):
                if(x is not type({})):
                    y = dict(y)
                yield x,y

    def set_price(self, exchange_name, market_name, coin_name, price, timestamp):
        exchange = self.price.get(exchange_name) if self.price.get(exchange_name) is not None else {}
        market = exchange.get(market_name) if exchange.get(market_name) is not None else {}
        coin = market.get(coin_name) if market.get(coin_name) is not None else {}
        coin['price'] = price
        coin['timestamp'] = timestamp
        
        market[coin_name] = coin
        exchange[market_name] = market
        self.price[exchange_name] = exchange
        
        
    def get_price(self, exchange_name, market_name, coin_name):
        
        if self.price.get(exchange_name) is not None:
            exchange = self.price.get(exchange_name) 
        else:
            return None
            
        if exchange.get(market_name) is not None:
            market = exchange.get(market_name) 
        else:
            return None
            
        if market.get(coin_name) is not None:
            coin = market.get(coin_name) 
        else:
            return None
            
        return coin
    

if __name__ == '__main__':
    print('Enviroments test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    ps = PriceStorage()
    
    ps.set_price('UPBIT', 'KRW', 'BTC', 10000000, 123)
    print(ps.get_price('UPBIT', 'KRW', 'BTC'))
    r = ps.get_price('UPBIT', 'KRW', 'BTC')
    print(type(r))
    print(r['price'])
    
    ps.set_price('UPBIT', 'KRW', 'BTC', 10000001, 123)
    print(ps.get_price('UPBIT', 'KRW', 'BTC'))
    print(ps.get_price('UPBIT', 'KRW', 'BTC'))
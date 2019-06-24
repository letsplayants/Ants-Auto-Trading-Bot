# -*- coding: utf-8 -*-

class OrderInfo():
    """
    {
        "Symbol" : "BTC/USDT",
        "id" : "970481e8-765b-4092-9047-2b42a9726458",
        "side" : "buy/sell",
        "price" : "1.7e-07",
        "amount" : "100000",
        "status" : "open",
        "remaining" : "11234", #오더 미체결 개수
        "status" : "open, close",
        "ts_create" : "1552493189043", #최초 오더 시간
        "ts_updated" : "111111111111", #마지막 업데이트 된 시간
        
    }
    """
    def __init__(self):
        self.symbol = ''
        self.id = ''
        self.side = ''
        self.price = ''
        self.amount = ''
        self.status = ''
        self.remaining = ''
        self.ts_create = ''
        self.ts_updated = ''
        self.exchange = ''
        self.from_who = ''
        self.etc = {}
        
        pass
    
    def set(self, symbol, id, side, price, amount, status, remaining, ts_create, ts_updated, exchange, _from, etc={}):
        self.symbol = symbol
        self.id = id
        self.side = side
        self.price = price
        self.amount = amount
        self.status = status
        self.remaining = remaining
        self.ts_create = ts_create
        self.ts_updated = ts_updated
        self.exchange = exchange
        self.from_who = _from
        self.etc = etc
        
    def __repr__(self):
        return str(dict(self))
        # return str({
        #     'symbol' : self.order['symbol'],
        #     'id': self.order['id'],
        #     'side': self.order['side'],
        #     'price': self.order['price'],
        #     'amount': self.order['amount'],
        #     'status': self.order['status'],
        #     'remaining': self.order['remaining'],
        #     'ts_create': self.order['ts_create'],
        #     'ts_updated': self.order['ts_updated']
        # })
       
    def __iter__(self):
        klass = self.__class__
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        iters.update(self.__dict__)

        exclude=['']
        for x,y in iters.items():
            if(x not in exclude):
                yield x,y
                
    def __getitem__(self, key):
        return getattr(self, key)
        
    def __setitem__(self, key, value):
        if(hasattr(self, key)):
            setattr(self, key, value)
        else:
            raise Exception(f'{key} is not exist')
    
if __name__ == '__main__':
    print('test')
    
    
    
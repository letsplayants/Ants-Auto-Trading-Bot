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
        self.order = {}
        pass
    
    def add(self, symbol, id, side, price, amount, status, remaining, ts_create, ts_updated):
        item = {}
        item['symbol'] = symbol
        item['id'] = id
        item['side'] = side
        item['price'] = price
        item['amount'] = amount
        item['status'] = status
        item['remaining'] = remaining
        item['ts_create'] = ts_create
        item['ts_updated'] = ts_updated
        
        self.order = item
        
    def get(self):
        return self.order
        
        
if __name__ == '__main__':
    print('test')
    
    
    
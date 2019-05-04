# -*- coding: utf-8 -*-
from exchangem.model.amount_model import AmountModel

class CoinModel():
    """
    """
    symbol = ''
    market = ''
    amount = AmountModel()
    
    def __init__(self, args={}):
        pass
    
    def __iter__(self):
        klass = self.__class__
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        iters.update(self.__dict__)

        for x,y in iters.items():
            if(type(y) == type(AmountModel())):
                y = dict(y)
            yield x, y

if __name__ == '__main__':
    print('CoinModel test')
    
    pm1 = CoinModel()
    pm2 = CoinModel()
    
    pm1.amount.available = 100
    pm1.amount.keep = 100
    
    print(dict(pm1))
    # print(dict(pm2))
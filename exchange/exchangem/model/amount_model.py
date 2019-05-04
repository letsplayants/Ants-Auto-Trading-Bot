# -*- coding: utf-8 -*-
class AmountModel():
    """
    available_amount : 한번에사용할 금액
    keep_amount : 남겨둘 금액
    """
    available = 0
    keep = 0
    
    def __init__(self):
        pass
    
    def __iter__(self):
        klass = self.__class__    
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        iters.update(self.__dict__)

        for x,y in iters.items():
            yield x,y

if __name__ == '__main__':
    print('AmountModel test')
    
    
    pm1 = AmountModel()
    pm2 = AmountModel()
    
    pm1.available = 10
    pm1.keep = 1.5
    
    print(dict(pm1))
    print(dict(pm2))
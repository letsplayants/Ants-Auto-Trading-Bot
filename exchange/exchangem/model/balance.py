# -*- coding: utf-8 -*-

class Balance():
    """
    {
        "KRW": {
            "total": 100,
            "used": 10,
            "free": 90
        },
        "BTC": {
            "total": 100,
            "used": 10,
            "free": 90
        }
    }
    """
    def __init__(self):
        self.balance = {}
        pass
    
    def add(self, name, total, used, free):
        item = {}
        item['total'] = total
        item['used'] = used
        item['free'] = free
        self.balance[name] = item
        
    def add_all(self, args):
        self.balance = args
        
    def get(self, target):
        return self.balance.get(target)
        
    def get_all(self):
        return self.balance
    
    def __repr__(self):
        return str(self.balance)
        
    def __str__(self):
        return str(self.balance)
        
if __name__ == '__main__':
    print('test')
    bal = Balance()
    
    bal.add('KRW', 100, 90, 10)
    bal.add('BTC', 200, 90, 110)
    print(bal.get('KRW'))
    print(bal.get_all())
    
    
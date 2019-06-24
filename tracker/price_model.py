# -*- coding: utf-8 -*-
import logging
import consts
import json
import sys

class PriceModel():
    """
        item['exchange']
        item['coin']
        item['market']
        item['target_price']
        item['high_eq_low'] 타겟가 이상 또는 이하
        item['callback'] 콜백함수
        item['raw'] = {
            'from' : 'tsb-34-10m',
            ...
        }
    """
    def __init__(self):
        self.exchange=''
        self.coin=''
        self.market=''
        self.target_price=''
        self.high_eq_low=''
        self.callback=None
        self.raw={}
        pass
    
    def from_dict(self, src):
        if(type(src) is not type({})):
            return
        
        for a, b in src.items():
            setattr(self, a, b)
        
        return self

    def __repr__(self):
        return str(dict(self))
        
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
    print('PriceModel test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    # import os
    # from env_server import Enviroments
    # path = os.path.dirname(__file__) + '/../configs/ant_auto.conf'
    # Enviroments().load_config(path)
    
    pm = PriceModel()
    pm['exchange']='upbit1'
    print(pm)
    json_str = json.dumps(dict(pm))
    print(json_str)
    
    ddict = json.loads(json_str)
    print(ddict)
    new_pm = PriceModel()
    revpm = new_pm.from_dict(ddict)
    print(new_pm)
    print(revpm)
    
    
    pm.raw={
        'from':'tsb3310m',
        'cb':['def1','def2'],
        'tree':{
            'tree1':1,
            'tree2':'2',
            'tree3':None
        }
    }
    print(pm)
    json_str = json.dumps(dict(pm))
    print(json_str)
    
    ddict = json.loads(json_str)
    print(ddict)
    new_pm = PriceModel()
    revpm = new_pm.from_dict(ddict)
    print(new_pm)
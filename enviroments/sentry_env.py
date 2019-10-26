# -*- coding: utf-8 -*-
import logging
import consts
import json
import sys

class SentryEnv(dict):
    """
    {
        sentry:{
            dsn: 'aaaaaaaaaaaaa'
        }
    }
    """
    def __init__(self):
        # self.__set_default__()
        pass
    
    # def __set_default__(self):
    #     self.sentry={
    #         "dsn": ""
    #     }
        
    # def __getitem__(self, key):
    #     return self.sentry.get(key)
        
    # def __setitem__(self, key, value):
    #     self.sentry[key] = value
    
    # def from_dict(self, src):
    #     if(type(src) is not type({})):
    #         return
        
    #     for a, b in src.items():
    #         setattr(self, a, b)

    # def __iter__(self):
    #     klass = self.__class__
    #     iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

    #     iters.update(self.__dict__)

    #     include=['sentry']
    #     for x,y in iters.items():
    #         if(x in include):
    #             yield x,y
                
    # def show_list(self):
    #     return self.sentry
        
    # def check_default(self):
    #     if(self.sentry is None):
    #         self.sentry = {}    
    #     pass
    
    # def set(self, key, val):
    #     self.sentry[key] = val
        
    # def get(self, key):
    #     return self.sentry.get(key)

    # def set_value(self, v):
    #     if(v.get('sentry') is None):
    #         nq = {}
            
    #     self.sentry = v.get('sentry')
        
if __name__ == '__main__':
    print('Enviroments test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    import os
    from env_server import Enviroments
    path = os.path.dirname(__file__) + '/../configs/ant_auto.conf'
    
    env = Enviroments()
    env.load_config(path)
    
    my_sentry = env.sentry
    print('sentry dsn : {}'.format(my_sentry['dsn']))
    
    
    
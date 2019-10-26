# -*- coding: utf-8 -*-
import logging
import consts
import json
import sys

import ants.utils as utils

class MessengerEnv(dict):
    """
    {
        "owner_id": "@lemy0715",
        "owner_name": "LeMY",
        "bot_id": "ants_chat_bot",
        "bot_token": "738520272:AAFm_svmDBERNLDsm0N9X75_y2ivOkR3k",
        "chat_id": "4449550",
        "authorized":["444609550", "444609550"]
    }
    """
    def __init__(self):
        pass
    
    # def __getitem__(self, key):
    #     return self.messenger.get(key)
        
    # def __setitem__(self, key, value):
    #     self.messenger[key] = value
    
    # def from_dict(self, src):
    #     if(type(src) is not type({})):
    #         return
        
    #     for a, b in src.items():
    #         setattr(self, a, b)

    # def __iter__(self):
    #     klass = self.__class__
    #     iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

    #     iters.update(self.__dict__)

    #     include=['messenger']
    #     for x,y in iters.items():
    #         yield x,y
    #         # if(x in include):
    #         #     yield x,y
            
    # def __repr__(self):
    #     return dict(self)
        
    # def __str__(self):
    #     return str(dict(self))
        
    # def show_list(self):
    #     return self.messenger
        
    # def check_default(self):
    #     if(self.messenger is None):
    #         self.messenger = {}
        
    # def get_messenger_env(self):
    #     return self.messenger

    # def add_chat_id(self, id):
    #     self.messenger['chat_id'] = id
    
    # def set_value(self, v):
    #     self.messenger = v['messenger']

    def load_v1_config(self):
        self.messenger = utils.readConfig('configs/telegram_bot.conf')

    # def get(self, key):
    #     return self.messenger.get(key)
    
    # def add_authorized(self, value):
    #     k = 'authorized'
    #     v = getattr(self, k, None)
    #     if(v is not None):
    #         v.append(value)
    #     else:
    #         v = value
            
    #     setattr(self, k, v)
    #     # self.authorized.append(value)    
        
    # def set_authorized(self, value):
    #     k = 'authorized'
    #     v = getattr(self, k, None)
    #     if(v is not None):
    #         v.append(value)
    #     else:
    #         v = value
            
    #     setattr(self, k, v)
    #     # self.authorized.append(value)
        
    # def remove_authorized(self, value):
    #     self.authorized.remove(value)
    
    # def get_authorized(self):
    #     return self.authorized
    
    def p(self):
        print('test')

if __name__ == '__main__':
    print('Enviroments test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    msg = MessengerEnv()
    # print(dict(msg))
    print('org : {}'.format(msg))
    
    import os
    from env_server import Enviroments
    path = os.path.dirname(__file__) + '/../configs/ant_auto.conf'
    Enviroments().load_config(path)
    
    env = Enviroments()
    
    idx = 0
    idx += 1
    print(idx, '-'*240)
    print('type : {}'.format(type(env.messenger)))
    print('data : {}'.format(env.messenger))
    print('func call')
    env.messenger.p()
    
    
    # idx += 1
    # print(idx, '-'*240)
    # env.messenger.add_chat_id('123')
    # print(env.messenger)
    # env.save_config()
    
    # env.messenger.set_authorized('auth1')
    # print(env.messenger.get_authorized())
    # print(env.messenger)
    # env.messenger.remove_authorized('auth1')
    
    # env.save_config()
    
    # tel_id='@lemy_bot'
    # messenger_q = {
    #     'telegrma_id': tel_id,
    #     'quick_trading': 'quick_trading'
    # }
    # Enviroments().qsystem['messenger'] = messenger_q
    
    # get_q = Enviroments().qsystem['messenger']
    # print('messenger_q:{}'.format(get_q['telegrma_id']))
    
    # print('qlist : {}'.format(Enviroments().qsystem.show_list()))
    
    
    # print(json.dumps(get_q))
    
    # qq = Qsystem()
    # print(json.dumps(qq))
    
    # qq = dict(Qsystem(Enviroments()))
    # json.dumps(qq)
    # # file.write(json.dumps(dict(self), indent=4, sort_keys=True))
    
    # # for i in Qsystem():
    # #     print(i)
        
        
    # Enviroments().save_config()
# -*- coding: utf-8 -*-
import logging
import consts
import json
import sys

class QsystemEnv(dict):
    """
    {
        
    }
    """
    def __init__(self, enviroments):
        # self.qlist={}
        self.enviroments = enviroments
        pass
    
    # def __getitem__(self, key):
    #     return self.qlist.get(key)
        
    # def __setitem__(self, key, value):
    #     self.qlist[key] = value
    
    # def from_dict(self, src):
    #     if(type(src) is not type({})):
    #         return
        
    #     for a, b in src.items():
    #         setattr(self, a, b)

    # def __iter__(self):
    #     klass = self.__class__
    #     iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

    #     iters.update(self.__dict__)

    #     include=['qlist']
    #     for x,y in iters.items():
    #         if(x in include):
    #             yield x,y
                
    # def show_list(self):
    #     return self.qlist
        
    # def check_default(self):
    #     pass
    
    def get_quicktrading_q(self):
        return 'messenger.telegram.{}.quick_trading'.format(self.enviroments.messenger['bot_token'])
    
    def get_telegram_messenge_q(self):
        return 'messenger.telegram.{}.message'.format(self.enviroments.messenger['bot_token'])
    
    def get_upgrade_q(self):
        return 'upgrade.{}'.format(self.enviroments.messenger['bot_token'])
    
    def get_database_q(self):
        return 'database.{}'.format(self.enviroments.messenger['bot_token'])
    
    # def set(self, key, val):
    #     self.qlist[key] = val
        
    # def get(self, key):
    #     return self.qlist.get(key)

    # def set_value(self, v):
    #     if(v.get('qlist') is None):
    #         nq = {}
            
    #     self.qlist = v.get('qlist')
        
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
    
    tel_id='@lemy_bot'
    messenger_q = {
        'telegrma_id': tel_id,
        'quick_trading': 'quick_trading'
    }
    env.qsystem['messenger'] = messenger_q
    
    get_q = env.qsystem['messenger']
    print('messenger_q:{}'.format(get_q['telegrma_id']))
    
    env.qsystem['db'] = 'database'
    # print('qlist : {}'.format(Enviroments().qsystem.show_list()))
    
    
    # print(json.dumps(get_q))
    
    # qq = Qsystem()
    # print(json.dumps(qq))
    
    qq = dict(QsystemEnv(env))
    json.dumps(qq)
    # file.write(json.dumps(dict(self), indent=4, sort_keys=True))
    
    # for i in Qsystem():
    #     print(i)
        
    print(env.qsystem.get_quicktrading_q())    
    # Enviroments().save_config()
    
    env.qsystem['tsb.314.45'] = 'tsb.314.45'
    print(env.qsystem.get('tsb.314.45'))
    # Enviroments().save_config()
    
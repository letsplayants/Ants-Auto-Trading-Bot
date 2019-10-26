# -*- coding: utf-8 -*-

import logging
import sentry_sdk

from env_server import Enviroments

class AntSentry():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchanges = {}
        self.dsn = Enviroments().sentry.get('dsn')
        self.logger.debug('sentry dsn : {}'.format(self.dsn))
        if(self.dsn is not None and self.dsn is not ''):
            self.init_sentry()
        pass
    
    def init_sentry(self):
        env = Enviroments()
        
        try:
            sentry_sdk.init(self.dsn)
        except Exception as e:
            self.logger.warning('Sentry({}) can not init cause {} :'.format(self.dsn, e))
            return
        
        owner_id = env.messenger.get('owner_id') if env.messenger.get('owner_id') != None else ''
        owner_name = env.messenger.get('owner_name') if env.messenger.get('owner_name') != None else ''
        bot_id = env.messenger.get('bot_id') if env.messenger.get('bot_id') != None else ''
        bot_name = env.messenger.get('bot_name') if env.messenger.get('bot_name') != None else ''
        
        with sentry_sdk.configure_scope() as scope:
            scope.user = {
                # "email": "자신의 연락처를 넣는다",
                "id" : owner_id,
                "username" : owner_name
            }
            scope.set_tag("telebot_id", bot_id)
            scope.set_tag("telebot_name", bot_name)
            _context = {
                "common": env.common,
                "messenger" : env.messenger,
                "qsystem": env.qsystem,
                "etc" : env.etc
            }
            scope.set_context("configuration", _context)
            
    
if __name__ == "__main__":
    print('Sentry test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    import os
    path = os.path.dirname(__file__) + '/../configs/ant_auto.conf'
    Enviroments().load_config(path)
            
    my_sentry = AntSentry()
    
    import sentry_sdk
    sentry_sdk.capture_message('Sentry Test')
    
    pass

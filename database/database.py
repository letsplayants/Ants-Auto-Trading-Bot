#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from env_server import Enviroments
from q_receiver import MQReceiver

class Database():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        env = Enviroments()
        env.load_config()
        
        self.subscriber_name = Enviroments().qsystem.get_database_q()
        self.subscriber = MQReceiver(self.subscriber_name, self.sbuscribe_message)
        self.subscriber.start()
        
    def sbuscribe_message(self, ch, method, properties, body):
        body =  body.decode("utf-8")
        #로그 폴더 파일에 무식하게 기록한다
        self.logger.debug('got message : {}'.format(body))
        with open('logs/trading_record' , "a") as f:
            f.write(f'{body}\n')

if __name__ == "__main__":
    print('Database test')
    Enviroments().load_config()
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("telegram.vendor.ptb_urllib3.urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.updater").setLevel(logging.WARNING)
    logging.getLogger("telegram.bot").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.dispatcher").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("JobQueue").setLevel(logging.WARNING)
    
    db = Database()
    
    from q_publisher import MQPublisher
    pub = MQPublisher(Enviroments().qsystem.get_database_q())
    
    pub.send('abc')
    

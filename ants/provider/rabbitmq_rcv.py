#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pika
import sys
import datetime
import time
import ants.utils as utils
import json
import logging
import threading

from ants.provider.provider import Provider
from messenger.q_receiver import MQReceiver

from env_server import Enviroments

class MQProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self.logger = logging.getLogger(__name__)
        
        self.exchange_name = Enviroments().qsystem.get_quicktrading_q()
        self.mq_receiver = MQReceiver(self.exchange_name, self.callback)
        
        self.isRun = False
        pass
    
    def callback(self, ch, method, properties, body):
        body =  body.decode("utf-8")
        try:
            ret = eval(body)
        except Exception as exp:
            self.logger.warning('Can''t converte {}'.format(body))
            ret = {}
        
        self.logger.debug('Received {}'.format(body))
        self.notify(ret)
    
    def register(self, update, coins):
        self.logger.info('register update')
        self.attach(update)
        pass
    
    def run(self):
        self.logger.info('Try MQ subscribe start')
        self.mq_receiver.start()
        pass
    
    def stop(self):
        self.logger.info('MQ provider will stop...')
        self.isRun = False
        self.mq_receiver.close()
        self.logger.info('MQ provider will stop.')
        pass
    

if __name__ == '__main__':
    print('MQ RCV test')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)

    import signal
    def signal_handler(sig, frame):
        print('\nExit Program by user Ctrl + C')
        mq.stop()
    
    signal.signal(signal.SIGINT, signal_handler)

    mq = MQProvider()
    # mq.load_setting('configs/mail.key')
    mq.run()
        
                
    



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

class MQProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.init_MQ()
        self.isRun = False
        # self.load_setting('configs/mail.key')
        pass
    
    def init_MQ(self):
        self.queue_name = 'trading_msg'
        self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        
    def callback(self, ch, method, properties, body):
        #TODO Message 분석 후 정상적인 메시지인지 확인
        body = str(body)
        _list = body.split('#')
        ret={}
        ret['market'] = _list[1].strip()
        ret['time'] = _list[2].strip()
        ret['action'] = _list[3].strip()
        ret['exchange'] = _list[4].strip()
        
        self.notify(ret)
        self.logger.debug(" Received {}".format(body))
    
    def register(self, update, coins):
        self.logger.info('register update')
        self.attach(update)
        pass
    
    
    def run(self):
        self.isRun = True
        self.logger.info('email provider run.')
        
        self.thread_hnd = threading.Thread(target=self._run, args=())
        self.thread_hnd.start()
        pass
    
    def stop(self):
        self.logger.info('MQ provider will stop...')
        self.isRun = False
        self.channel.close() #block 방식의 쓰레딩이므로 그냥 닫아버려서 오류를 유도한다
        self.thread_hnd.join()
        self.logger.info('MQ provider will stop.')
        pass
    
    def _run(self):
        while(self.isRun):
            self.logger.debug(' [*] Waiting for messages. To exit press CTRL+C')
            self.channel.start_consuming()
            
    
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
        
                
    



import pika
import logging
import time

class MQPublisher():
    def __init__(self, exchange_name=None):
        self.logger = logging.getLogger(__name__)
        self.g_cnt = 0
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        if(exchange_name is not None):
            self.make_exchange(exchange_name)
        pass

    def get_exchange_name(self):
        return self.exchange_name
    
    def make_exchange(self, exchange_name):
        if(exchange_name is not None):
            self.exchange_name = exchange_name
        
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name,
                            exchange_type='fanout',
                            passive=False, durable=False, auto_delete=False)
    
    
    def send(self, message):
        if(type(message) is dict):
            message = str(message)
            
        if self.connection.is_closed or self.connection.is_closing or self.channel is None or not self.channel.is_open:
            self.make_exchange(self.exchange_name)
        
        self.logger.debug('send msg : {}'.format(message))
        #연결이 끊히는 예외가 있다
        try:
            self.channel.basic_publish(exchange=self.exchange_name,
                                        routing_key='',
                                        body=message)
        except Exception as exp:
            self.logger.warning('send exception : {}'.format(exp))
            if(self.g_cnt > 10):
                raise Exception(exp)
            
            time.sleep(1)
            self.g_cnt += 1
            self.make_exchange(self.exchange_name)
            self.send(message)
            return
        
        self.g_cnt = 0
    
    def close(self):
        self.connection.close()
    
if __name__ == '__main__':
    print('exchange publisher test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("pika").setLevel(logging.WARNING)
    
    queue_name = 'trading_msg'
    # queue_name = 'messenger.telegram.quick_trading'
    message = '#BTC/KRW #1D #BUY #UPBIT #AUTO'
    
    pub = MQPublisher(queue_name)
    # pub.send(message)
    
    import time
    while(True):
        pub.send({
                    'action' : 'buy',
                    'exchange': 'upbit'
        })
        time.sleep(600)
    
    pub.close()
    
    # print(pub.__module__)
    # print(id(pub))
    # print(dir(pub))
    # print(globals())
    # print(locals())
    
    # print(class(pub))
    
    
    
    


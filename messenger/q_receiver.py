import pika
import threading
import logging

class MQReceiver():
    def __init__(self, exchange_name=None, callback=None):
        self.logger = logging.getLogger(__name__)
        self.loop = True
        if(exchange_name is not None and callback is not None):
            self.make_exchange(exchange_name, callback)
        pass
    
    def get_exchange_name(self):
        return self.exchange_name
    
    def callback_chain(self, ch, methode, properties, body):
        self.logger.debug('got message : {}'.format(body))
        self.regist_callback(ch, methode, properties, body)
        
    def make_exchange(self, exchange_name, callback):
        if(exchange_name is not None and callback is not None):
            self.exchange_name = exchange_name
            self.regist_callback = callback
        
        self.logger.info('exchange binding with {}, {}'.format(self.exchange_name, self.regist_callback))
        
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=180))
        self.channel = self.connection.channel()
            
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
        result = self.channel.queue_declare('', exclusive=True, auto_delete=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        self.channel.basic_consume(
                queue=queue_name, on_message_callback=self.callback_chain, auto_ack=True)
    
    def start(self):
        self.thread_hnd = threading.Thread(target=self._run, args=())
        self.thread_hnd.start()
        
    def _run(self):
        while(self.loop):
            try:
                self.channel.start_consuming()
            except Exception as exp:
                self.logger.warning('Q consuming has exception cause : \n{}'.format(exp))
            
            time.sleep(10)
            self.make_exchange(self.exchange_name, self.regist_callback)
            
        
    def stop(self):
        self.loop = False
        self.close()
        
    def close(self):
        self.loop = False
        try:
            self.channel.close()
        except :
            self.logger.warning('exception..')
            
        # while self.channel._consumer_infos:
        #     self.channel.connection.process_data_events(time_limit=1) # 1 second
    
        self.thread_hnd.join()
        # self.connection.close()
        
if __name__ == '__main__':
    print('strategy test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    queue_name = 'trading_msg'
    
    def callback(ch, methode, properties, body):
        print('get message :', body)
    
    recv = MQReceiver(queue_name, callback)
    recv.start()
    
    


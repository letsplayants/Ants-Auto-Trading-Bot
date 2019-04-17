import pika
import threading

class MQReceiver():
    def __init__(self, exchange_name=None, callback=None):
        if(exchange_name is not None and callback is not None):
            self.make_exchange(exchange_name, callback)
        pass
    
    def get_exchange_name(self):
        return self.exchange_name
    
    def make_exchange(self, exchange_name, callback):
        if(exchange_name is not None and callback is not None):
            self.exchange_name = exchange_name
            self.callback = callback
            
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=5))
        self.channel = self.connection.channel()
            
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
        result = self.channel.queue_declare('', exclusive=True, auto_delete=False)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        self.channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    def start(self):
        self.thread_hnd = threading.Thread(target=self._run, args=())
        self.thread_hnd.start()
        
    def _run(self):
        self.channel.start_consuming()
        
    def stop(self):
        self.close()
        
    def close(self):
        self.thread_hnd.join()
        self.connection.close()
        
if __name__ == '__main__':
    print('strategy test')
    queue_name = 'trading_msg'
    
    def callback(ch, methode, properties, body):
        print('get message :', body)
    
    recv = MQReceiver(queue_name, callback)
    recv.start()
    
    


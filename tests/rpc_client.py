#!/usr/bin/env python
import pika
import uuid

class FibonacciRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare('', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, func, *kwargs):
        body = {
            'func': func,
            'args': kwargs
        }
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue.ext',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(body))
        while self.response is None:
            self.connection.process_data_events()
            
        response = self.response.decode()
        return response

fibonacci_rpc = FibonacciRpcClient()

response = fibonacci_rpc.call('p1', 'abc', 30)
print("1 [.] Got %r" % response)

response = fibonacci_rpc.call('p2', 30, 'abc', 'aaa')
print("2 [.] Got %r" % response)

response = fibonacci_rpc.call('notexistfunc', 30, 'abc')
print("3 [.] Got %r" % response)

response = fibonacci_rpc.call('p2', [1,2,3], 'abc', 'aaa')
print("2 [.] Got %r" % response)

response = fibonacci_rpc.call('p2', {'dict':'type1', 'd2':2}, 'abc', 'aaa')
print("2 [.] Got %r" % response)

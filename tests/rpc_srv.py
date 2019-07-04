# -*- coding: utf-8 -*-
#!/usr/bin/env python
import pika

class RPC_M():
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue.ext')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='rpc_queue.ext', on_message_callback=self.on_request)
        
        self.__method_list__()
    
    def on_request(self, ch, method, props, body):
        # print(f'method : {method}')
        # print(f'props : {props}')
        # print(f'body : {body}')
        
        body = eval(body.decode())
        # print(f'body : {type(body)}')
        
        func = body['func']
        #클래스 메소드에서 이름을 찾는다
        response = self.__call_method__(body['func'], body['args'])
        
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                         body=response)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def __method_list__(self):
        klass = self.__class__
        self.method_list = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and callable(y))
        
        print('{} method_list : {}'.format(self.__class__, self.method_list))
        
    
    def __call_method__(self, func_name, args):
        if(func_name not in self.method_list):
            return 'Exception : function is not exist : {}'.format(func_name)
        
        try:
            print('{} call with {}'.format(func_name, args))
            func = self.method_list[func_name]
            ret = func(self, *args)
        except Exception as exp:
            print(exp)
            return str(exp)
        
        return str(ret)
    
    def run(self):
        self.channel.start_consuming()
        
    def p1(self, *args):
        return f'server method 1 with {args}'
    
    def p2(self, arg1, arg2, arg3):
        return f'server method 2 with {arg1, arg2, arg3}'


print(" [x] Awaiting RPC requests")
rpc = RPC_M()
rpc.run()
import pika

queue_name = 'trading_msg'
# message = '#BTC/KRW #1M #BUY #UPBIT'
message = '#BTC/KRW #1D #BUY #UPBIT #AUTO'
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

channel.basic_publish(exchange='',
                      routing_key=queue_name,
                      body=message)
                      
print(" [x] Sent 'Hello World!'")

connection.close()


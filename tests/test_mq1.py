from q_publisher import MQReceiver
from q_receiver import MQPublisher


pub = MQPublisher('test.rcptest')
sub = MQReceiver('test.rcptest')


rpc_srv.register_rpc(func1)
rpc.call(func1)



print(bot.first_name)
print(bot.get_me())
print(bot.get_me()['username'])
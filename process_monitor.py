# -*- coding: utf-8 -*-
import ants.prj_path
import os, sys
import subprocess
import time
from subprocess import Popen, PIPE
from q_receiver import MQReceiver
from env_server import Enviroments

Enviroments().load_config()
proc = None

def sbuscribe_message(ch, method, properties, body):
    print('got message : {}'.format(body))
    body =  body.decode("utf-8")
    if(body.find('restart') == 0):
        os.kill(proc.pid, 3)

subscriber_name = Enviroments().qsystem.get_upgrade_q()
subscriber = MQReceiver(subscriber_name, sbuscribe_message).start()

current_pwd = os.getcwd() + '/'
main_py = current_pwd + 'ants/main.py'

command = 'python3'
su = ''
if(current_pwd.find('/home/pi/') == 0):
    #라즈베리파이로 인식한다
    #라즈베리파이의 경우 python3으로 구동하면 시스템 기본인 3.5 버젼으로 구동된다
    #최초 OS 설정 때 3.6버젼을 python으로 맵핑해 둔 상황이다.
    #그러므로 python으로 구동한다
    command = 'python'

while(True):
    try:
        proc = Popen([command, main_py], stdout=PIPE, universal_newlines=True)
    except Exception as exp:
        print('Can''t start {} with exception : {}'.format(main_py, exp))
        sys.exit(1)
    
    proc.wait()
    
    print('proc terminated. it will be restart')

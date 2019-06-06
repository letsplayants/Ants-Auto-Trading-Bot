# -*- coding: utf-8 -*-
import ants.prj_path
import logging
import logging.config
import json
import os, sys
import subprocess
import time
import signal
from subprocess import Popen, PIPE
from q_receiver import MQReceiver
from env_server import Enviroments

if __name__ == "__main__":
    logging.basicConfig()
    try:
        with open("configs/watcher.log.conf", "r") as fd:
            logging.config.dictConfig(json.load(fd))
    except Exception as ex:
        print(ex)
        print("Can't load log.conf file")
        logging.config.dictConfig(DEFAULT_CONFIG)
        pass
    logger = logging.getLogger()  # Returns the "root" logger
    
    logger = logging.getLogger('ANT_PROCESS_WATCHER')
    Enviroments().load_config()
    proc = None
    looping = True
    
    
    def sbuscribe_message(ch, method, properties, body):
        logger.info('got message : {}'.format(body))
        body =  body.decode("utf-8")
        if(body.find('restart') == 0):
            child_pid = proc.pid
            logger.info('child process({}) kill'.format(child_pid))
            os.kill(child_pid, signal.SIGTERM)
            
    
    subscriber_name = Enviroments().qsystem.get_upgrade_q()
    subscriber = MQReceiver(subscriber_name, sbuscribe_message).start()
    logger.info('MQ Ready : {}'.format(subscriber_name))
    
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
        logger.info('This system is raspberry')
    
    
    def signal_handler(sig, frame):
        logger.info('Program will exit by {}'.format(sig))
        global looping
        looping = False
        
        child_pid = proc.pid
        logger.info('child process({}) kill'.format(child_pid))
        os.kill(child_pid, signal.SIGTERM)
        
        logger.info('Program Exit : {}'.format(looping))
    
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    
    def _exit():
        try:
            sys.exit()
        except SystemExit as exp:
            print('Exception SystemExit : {}'.format(exp))
            raise Exception()
        except:
            raise Exception()
    
    while(looping):
        try:
            proc = Popen([command, main_py])
        except Exception as exp:
            logger.error('Can''t start {} with exception : {}'.format(main_py, exp))
            sys.exit(1)
        
        proc.wait()
        
        logger.info('proc terminated. it will be restart : {}'.format(looping))
    
    logger.info('Program Exited')
    os._exit(0)
    # _exit()

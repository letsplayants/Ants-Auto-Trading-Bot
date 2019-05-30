# -*- coding: utf-8 -*-
import os, sys
import subprocess
import time

from subprocess import Popen, PIPE
current_pwd = os.getcwd() + '/'
main_py = current_pwd + 'ants/main.py'

su = ''
if(current_pwd.find('/home/pi/') == 0):
    #라즈베리파이로 인식한다
    su = 'sudo '
    
while(True):
    try:
        command = '{}python3'.format(su)
        proc = Popen([command, main_py], stdout=PIPE, universal_newlines=True)
    except Exception as exp:
        print('Can''t start {} with exception : {}'.format(main_py, exp))
        sys.exit(1)
    
    proc.wait()
    
    print('proc terminated. it will be restart')

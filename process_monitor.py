# -*- coding: utf-8 -*-
import os, sys
import subprocess
import time

from subprocess import Popen, PIPE
current_pwd = os.getcwd() + '/'
main_py = current_pwd + 'ants/main.py'

while(True):
    try:
        proc = Popen(["python3", main_py], stdout=PIPE, universal_newlines=True)
    except Exception as exp:
        print('Can''t start {} with exception : {}'.format(main_py, exp))
        sys.exit(1)
    
    proc.wait()
    
    print('proc terminated. it will be restart')

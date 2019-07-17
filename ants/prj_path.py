# -*- coding: utf-8 -*-
import sys
import os
from os.path import dirname
import logging

basePath = os.getcwd()
exchanges = basePath + '/exchange'
messenger = basePath + '/messenger'
enviroments = basePath + '/enviroments'
database = basePath + '/database'
tracker = basePath + '/tracker'

sys.path.insert(0, basePath)
sys.path.append(exchanges)
sys.path.append(messenger)
sys.path.append(enviroments)
sys.path.append(database)
sys.path.append(tracker)

logger = logging.getLogger(__name__)

logger.info(sys.path)
print ('sys path : '.format(sys.path))
print ('current path : '.format(os.getcwd()))

from enviroments.env_server import Enviroments

env = Enviroments()
env.sys['path'] = sys.path
env.sys['pwd'] = os.getcwd()


if __name__ == '__main__':
    print('Enviroments test')
    
    env = Enviroments()
    print(env)


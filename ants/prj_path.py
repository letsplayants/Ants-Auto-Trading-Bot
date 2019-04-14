# -*- coding: utf-8 -*-
import sys
import os
from os.path import dirname
import logging

basePath = os.getcwd()
exchanges = basePath + '/exchange'
messenger = basePath + '/messenger'

sys.path.insert(0, basePath)
sys.path.append(exchanges)
sys.path.append(messenger)

logger = logging.getLogger(__name__)

logger.info(sys.path)
print (sys.path)
print (os.getcwd())


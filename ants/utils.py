# -*- coding: utf-8 -*-

import sys  
import os
import json
import locale
import logging

logger = logging.getLogger(__name__)

def readConfig(filePath):
    return readKey(filePath)
    
def readKey(filePath):
    logger.info('read file {}'.format(filePath))
    if not os.path.isfile(filePath):
        logger.error("File path {} does not exist. Exiting...".format(filePath))
        raise Exception('File not found : {}'.format(filePath))
    
    try:
        with open(filePath) as fp:
            result = json.load(fp)
    except Exception as exp:
        logger.error("Can't load json : {}".format(exp))
        raise Exception('File format was wrong : {}'.format(exp))

    return result

def saveBinFile(fileName, data):
    f = open(fileName,'wb')
    f.write(data)
    f.close()
    
def loadBinFile(fileName): 
    f = open(fileName,'rb')
    data = f.read()
    f.close()
    return data
    
def krwFormat(number) :
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))
# -*- coding: utf-8 -*-

import sys  
import os
import json
import locale
import logging

logger = logging.getLogger(__name__)

class Util:
    @staticmethod
    def readKey(filePath):
        logger.info('read file {}'.format(filePath))
        if not os.path.isfile(filePath):
            logger.error("File path {} does not exist. Exiting...".format(filePath))
            sys.exit(1)
        
        try:
            with open(filePath) as fp:
                result = json.load(fp)
        except Exception as exp:
            logger.error("Can't load json : {}".format(exp))
            logger.error("Program exit")
            sys.exit(1)
    
        return result
    
    def saveBinFile(self, fileName, data):
        f = open(fileName,'wb')
        f.write(data)
        f.close()
        
    def loadBinFile(self, fileName): 
        f = open(fileName,'rb')
        data = f.read()
        f.close()
        return data
        
    def krwFormat(self, number) :
        s = '%d' % number
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + ','.join(reversed(groups))

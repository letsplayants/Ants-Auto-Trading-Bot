#!/usr/bin/env python
# -*- coding: utf-8 -*-

import prj_path
import signal
import alogger
import logging
from worker import Worker

if __name__ == "__main__":
    logger = logging.getLogger('ANT_MAIN')
    
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        w.stop()
        logger.info('Program Exit')

    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info('Program Start')
    w = Worker()
    w.run()
    pass

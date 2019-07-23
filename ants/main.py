#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sentry_sdk

import prj_path
import signal
import alogger
import logging
from telegram_repoter import TelegramRepoter
from database import Database
from env_server import Enviroments
from worker import Worker

if __name__ == "__main__":
    # sentry_sdk.init("https://2cdb19291410469cbec38e3af915bcc5@sentry.io/1502212")
    sentry_sdk.init("http://fcd237000f654835a24a428fcd076952@lemy0715dev.clserverer.com:15704/3")
    logger = logging.getLogger('ANT_MAIN')
    
    env = Enviroments()
    env.load_config()
    
    env.save_config()
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        tel.stop()
        w.stop()
        logger.info('Program Exit')

    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info('Program Starting')
    tel = TelegramRepoter()
    Database()
    
    w = Worker()
    w.run()
    
    
    pass

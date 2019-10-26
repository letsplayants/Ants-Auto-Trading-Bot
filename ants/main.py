# -*- coding: utf-8 -*-
import prj_path
import signal
import alogger
import logging
from telegram_repoter import TelegramRepoter
from database import Database
from env_server import Enviroments
from worker import Worker
from ant_sentry import AntSentry

if __name__ == "__main__":
    logger = logging.getLogger('ANT_MAIN')
    
    env = Enviroments()
    env.load_config()
    
    sentry = AntSentry()
    
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

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
    
    with sentry_sdk.configure_scope() as scope:
        scope.user = {
            "email": "자신의 연락처를 넣는다",
            "id" : "텔레방그램 자신의 user id를 넣는다",
            'username' : '텔레그램 user name을 넣는다'
        }
        scope.set_tag("telebot_id", "봇 id를 넣는다")
        scope.set_tag("telebot_name", "봇 이름을 넣는다")
        scope.set_context("configuration", {"strategi": "bar"})
    
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

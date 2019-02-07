# -*- coding: utf-8 -*-
# Parsing of Telegram Message

import telegram
from utils import readKey
import logging


logger = logging.getLogger(__name__)
token = ''
chat_id = ''
use = False
bot = None

def __initModule():
    try:
        mtoken = readKey('./configs/telegram_bot.key')
        
        try:
            global use
            use = False
            if(mtoken['use'].upper() == 'TRUE') :
                use = True
            else :
                logger.info('Telegram disable')
                return
            
            global token
            global chat_id
            global bot
            token = mtoken['bot_token']
            chat_id = mtoken['chat_id']
            bot = telegram.Bot(token=mtoken["bot_token"])
            logger.info(bot.get_me())
            bot.sendMessage(chat_id, 'Ant\'s telegram bot ready.')
        except Exception as exp:
            logger.warning('Telegram setting error : {}'.format(exp))
            use = False
    
    except Exception as exp:
        logger.warning('Telegram setting error : {}'.format(exp))
        use = False

class AntTelegram:
    def sendMessage(self, msg):
        logger.debug('sendMessage : {}'.format(use))
        if(use) :
            logger.debug('sendMsg : {}-{}'.format(chat_id, msg))
            bot.sendMessage(chat_id, msg)
        

__initModule()

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)

    tel = AntTelegram()
    tel.sendMessage("봇클래스 테스트.")

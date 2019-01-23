#Telegram에서 수신된 메시지를 파싱한다

import telegram
from utils import readKey
import logging


logger = logging.getLogger(__name__)
mtoken = readKey('./configs/telegram_bot.key')
token = mtoken['bot_token']
chat_id = mtoken['chat_id']
use = mtoken['use'].upper()
bot = telegram.Bot(token=mtoken["bot_token"])
logger.info(bot.get_me())

class AntTelegram:
    def sendMessage(self, msg):
        if(use == 'TRUE') :
            logger.debug('sendMsg : {}-{}')
            bot.sendMessage(chat_id, msg)
        

if __name__ == '__main__':
    bot.sendMessage(chat_id = -241706808, text="저는 봇입니다.")

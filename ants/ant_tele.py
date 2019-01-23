#Telegram에서 수신된 메시지를 파싱한다

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
            use = False
            if(mtoken['use'].upper() == 'TRUE') :
                use = True
            else :
                logger.info('Telegram disable')
                return
                
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
            logger.debug('sendMsg : {}-{}')
            bot.sendMessage(chat_id, msg)
        

__initModule()

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    tel = AntTelegram()
    tel.sendMessage("저는 봇클래스 테스트.")

# -*- coding: utf-8 -*-
# https://github.com/python-telegram-bot/python-telegram-bot

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ants.utils as utils
import logging

class TelegramRepoter():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        try:
            mtoken = utils.readConfig('configs/telegram_bot.conf')
            
            if(mtoken['use'].upper() == 'TRUE'):
                self.use = True
            else:
                self.logger.info('Telegram disable')
                return
            
            self.token = mtoken['bot_token']
            self.chat_id = mtoken['chat_id']
            self.bot = telegram.Bot(token=mtoken["bot_token"])
            
            self.logger.info('Telegram is Ready, {}'.format(self.bot.get_me()))

        except Exception as exp:
            self.logger.warning('Can''t load Telegram Config : {}'.format(exp))
            self.use = False
            return
        
    def run_listener(self):
        self.updater = Updater(self.token)
        dp = self.updater.dispatcher
        
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        
        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.echo))
        
        # log all errors
        dp.add_error_handler(self.error)
        
        # Start the Bot
        # 내부적으로 쓰레드로 처리된다.
        # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/updater.py
        self.updater.start_polling()
    
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
        
    def sendMessage(self, msg):
        logger.debug('sendMessage : {}'.format(self.use))
        if(self.use) :
            logger.debug('sendMsg : {}-{}'.format(self.chat_id, msg))
            self.bot.sendMessage(self.chat_id, msg)
    
    def start(self, update, context):
        """Send a message when the command /start is issued."""
        context.message.reply_text('Hi!')

    
    def help(self, update, context):
        """Send a message when the command /help is issued."""
        context.message.reply_text('Help!')
    
    
    def echo(self, update, context):
        """Echo the user message."""
        # update is bot
        # context is <class 'telegram.update.Update'>
        # context.message is <class 'telegram.message.Message'>
        # bot.send_message(update.message.chat_id, *args, **kwargs)
        print(type(context)) 
        # print(update.get_me())
        # print(getattr(update))
        print(type(context.message.reply_text))
        # print(update.message.replay_text)
        context.message.reply_text(context.message.text)
    
    
    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)
    

if __name__ == '__main__':
    print('strategy test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("telegram.vendor.ptb_urllib3.urllib3.connectionpool").setLevel(logging.WARNING)
    
    tel = TelegramRepoter()

    # tel.sendMessage("봇클래스 테스트.")

    tel.run_listener()
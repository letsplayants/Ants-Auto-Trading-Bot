# -*- coding: utf-8 -*-
# https://github.com/python-telegram-bot/python-telegram-bot

from signal import signal, SIGINT, SIGTERM, SIGABRT

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import ants.utils as utils
import logging
import json
import m_emoji as em
from menus.main_menu import MainMenu

class TelegramRepoter():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.menu_string_set()
        
        try:
            mtoken = utils.readConfig('configs/telegram_bot.conf')
            
            if(mtoken['use'].upper() == 'TRUE'):
                self.use = True
            else:
                self.use = False
                self.logger.info('Telegram disable')
                return
            
            self.token = mtoken['bot_token']
            self.chat_id = mtoken['chat_id']
            self.bot = telegram.Bot(token=mtoken["bot_token"])
        except Exception as exp:
            self.logger.warning('Can''t load Telegram Config : {}'.format(exp))
            self.use = False
            return
        
        self.menu_stack = []
        self.logger.info('Telegram is Ready, {}'.format(self.bot.get_me()))
        # self.send_message('Telegram Repoter is ready')
        self.run_listener()
        # self.remove_kdb()
        self.make_menu_keyboard()
        
        
    def menu_string_set(self):
        self.menu = MainMenu()
    
    
    def make_menu_keyboard(self, bot = None, chat_id = None):
        keyboard = []
        for item in self.menu:
            keyboard.append(InlineKeyboardButton(item))

        #ReplyKeyboardMarkup는 callback 기능이 없다.
        #그러므로 문구가 메뉴 호출에 해당한다
        #봇이 제공하는 버튼은 사용자가 채팅을 치는 것을 대신할 뿐이다.
        #봇이 버튼에서 '인사'라는 버튼을 제공한다면 사용자는 버튼을 누르는 것 대신 '인사'라고 쳐도 봇은 동일하게 동작한다
        
        self.welcome_message = '안녕하세요, 현재 버젼은 개발버젼입니다. 저는 다음과 같은 기능을 제공합니다'
        reply_markup = telegram.ReplyKeyboardMarkup(self.build_menu(keyboard, n_cols=2))
        self.bot.send_message(chat_id=self.chat_id, text=self.welcome_message, reply_markup=reply_markup)
  
    def message_parser(self, update, context):
        #받은 메시지를 해당 클래스에 전달함
        message = context.message
        text = message.text
        self.logger.debug(message.text)
        
        menu_item = None
        for item in self.menu:
            item_txt = str(item)
            if(item_txt == text):
                self.logger.debug("item : {}\t text: {}\t{}".format(item_txt, text, (item_txt == text)))
                menu_item = item
                self.menu_stack.append(item)
                break;
        
        self.logger.debug('fined item : {}'.format(menu_item))
        if(menu_item is None):
            return
        
        # 방법1. 동작안함. dp.restart 해야하는데, stop이후 start하면 뻗음.. 설령 stop이 된다고 하더라도 내부적으로 thread라 join되는데 기다리는데 시간이 많이 걸림
        # 현재 메시지 처리기를 지우고 하위 메뉴의 메시지 처리기를 등록해준다
        # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/dispatcher.py
        dp = self.updater.dispatcher
        
        menu_item.set_previous_message_handler(dp, self.message_handler)
        menu_item.set_previous_keyboard(self.make_menu_keyboard)
        menu_item.make_menu_keyboard(self.bot, self.chat_id)
        dp.add_handler(menu_item.message_handler)
        dp.remove_handler(self.message_handler)
        
        # menu_item.parsering(update, text)
        

    def build_menu(self,
               buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu
    
    def remove_kdb(self):
        """
        사용할 일 없을듯.
        """
        reply_markup = telegram.ReplyKeyboardRemove()
        self.bot.send_message(chat_id=self.chat_id, text="I'm back.", reply_markup=reply_markup)
    
    
    def run_listener(self):
        if(self.use == False):
            return
        
        self.updater = Updater(self.token)
        dp = self.updater.dispatcher
        
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("menu", self.menu))
        # dp.add_handler(CommandHandler("help", self.help))
        # dp.add_handler(CommandHandler("whoami", self.whoami))
        # dp.add_handler(CommandHandler("room", self.roominfo))
        # dp.add_handler(CommandHandler("setid", self.setid))
        
        dp.add_handler(CallbackQueryHandler(self.whoami, pattern='whoami'))
        dp.add_handler(CallbackQueryHandler(self.roominfo, pattern='roominfo'))
        dp.add_handler(CallbackQueryHandler(self.setid, pattern='setid'))
        #총 수익
        #오늘 수익
        #거래소 잔고
        #거래소 오더 상황(미체결)
        #거래소 동작(빤스런, 올매수)
        #거래소 스탑로스 설정 및 동작
        #inline keyboard를 사용하여 명령어 제어
        
        # on noncommand i.e message - echo the message on Telegram
        self.message_handler = MessageHandler(Filters.text, self.message_parser)
        dp.add_handler(self.message_handler)
        
        # log all errors
        dp.add_error_handler(self.error)
        
        # Start the Bot
        # 내부적으로 쓰레드로 처리된다.
        # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/updater.py
        self.updater.start_polling()
    
        # self.updater.idle()
    
    def stop_listener(self):
        self.logger.info('telegram will be stop')
        self.updater.signal_handler(SIGINT, 0)
    
    def menu(self, update, context):
        context.message.reply_text('Please choose:', reply_markup=self.menu_keyboard())
        
    def menu_keyboard(self):
        keyboard = [[InlineKeyboardButton("내 ID 정보", callback_data='whoami'),
                    InlineKeyboardButton("현재 방 정보", callback_data='roominfo')],
                    [InlineKeyboardButton("환영 인사", callback_data='setid')]]

        return InlineKeyboardMarkup(keyboard)
        
    def button(self, update, context):
        query = context.callback_query
        query.edit_message_text(text="Selected option: {}".format(query.data))
    
        
    def send_message(self, msg):
        self.logger.debug('send_message : {}'.format(self.use))
        if(self.use) :
            self.logger.debug('send_msg : {}-{}'.format(self.chat_id, msg))
            self.bot.sendMessage(self.chat_id, msg)
    
    def roominfo(self, update, context):
        query = context.callback_query
        
        self.edit_message(update, query, '방(Group) 속성 : {}\n Group id : {}'.format(query.message.chat.type, query.message.chat.id))
        
        
    def whoami(self, update, context):
        print('get message in whoami')
        query = context.callback_query
        if(query.message.chat.type != 'private'):
            self.edit_message(update, query, '1:1방에서만 설정 가능합니다')
            return
        self.edit_message(update, query, '당신의 ID : {}'.format(query.message.chat.id))

    def edit_message(self, bot, query, msg):
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=msg,
                        reply_markup=self.menu_keyboard())
    
    def setid(self, update, context):
        query = context.callback_query
        
        user = query.from_user
        msg = '환영합니다. {}님'.format(user.first_name)
        self.edit_message(update, query, msg)
    
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
    
    
    def error(self, bot_info, update, message):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', bot_info, message)
    

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
    logging.getLogger("telegram.ext.updater").setLevel(logging.WARNING)
    logging.getLogger("telegram.bot").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.dispatcher").setLevel(logging.WARNING)
    
    tel = TelegramRepoter()

    # tel.send_message("봇클래스 테스트.")

    # tel.run_listener()
    
    import signal
    from time import sleep
    def signal_handler(sig, frame):
        logger.info('Program will exit by user Ctrl + C')
        # w.stop()
        tel.stop_listener()
        logger.info('Program Exit')

    signal.signal(signal.SIGINT, signal_handler)
    
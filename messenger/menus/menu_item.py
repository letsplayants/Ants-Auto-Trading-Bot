import abc
import logging

from menus.m_iter import MIterators
from menus.menu_back import BackMenu

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class MenuItem(MIterators, metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(self.__class__.__module__, self.__class__.__name__))
        self.message_handler = MessageHandler(Filters.text, self.parsering)
        self.previous_msg_hnd = None
        self.dispatcher = None
        pass
    
    def init(self):
        pass
    
    @abc.abstractmethod
    def to_dict(self):
        """
        텔레그램 인라인 키보드에서 json으로 변환할 때 to_dict를 호출함
        이 때 리턴되는 문자열을 인라인 키보드에서 표시함
        """
        pass
        
    def get_message_handler(self):
        return self.message_handler
        
    def set_previous_message_handler(self, dispatcher, hnd):
        self.dispatcher = dispatcher
        self.previous_msg_hnd = hnd
    
    def set_previous_keyboard(self, kbd):
        self.previous_kbd = kbd
    
    def parsering(self, update, context):
        # 이 메뉴에서 사용하는 키보드를 만든다.
        # back이 눌리면 이전 키보드를 돌려준다.
        # 그 외 핸들러들을 등록해준다.
        message = context.message
        text = message.text
        self.logger.debug(message.text)
        
        menu_item = None
        for item in self.m_list:
            item_txt = str(item)
            # self.logger.debug("item : {}\t text: {}\t{}".format(item_txt, text, (item_txt == text)))
            if(item_txt == text):
                menu_item = item
                break;
        
        # self.logger.debug('fined item : {}'.format(menu_item))
        if(menu_item is None):
            return
        
        if(type(menu_item) == BackMenu):
            # self.logger.debug('back item : {}'.format(menu_item))
            #키보드 복구
            self.previous_kbd(self.bot, self.chat_id)
            
            #메시지 핸들러 복구
            self.dispatcher.add_handler(self.previous_msg_hnd)
            self.dispatcher.remove_handler(self.message_handler)
            return True
        
        #하위 메시지 핸들러를 등록하고 현재 메시지 핸들러를 제거한다
        menu_item.init()
        menu_item.set_previous_keyboard(self.make_menu_keyboard)
        menu_item.set_previous_message_handler(self.dispatcher, self.message_handler)
        menu_item.make_menu_keyboard(self.bot, self.chat_id)
        self.dispatcher.add_handler(menu_item.message_handler)
        
        self.dispatcher.remove_handler(self.message_handler)
     
    def go_back(self):
        # self.logger.debug('back item : {}'.format(menu_item))
        #키보드 복구
        self.previous_kbd(self.bot, self.chat_id)
        
        #메시지 핸들러 복구
        self.dispatcher.add_handler(self.previous_msg_hnd)
        self.dispatcher.remove_handler(self.message_handler)
        return
        
    def make_menu_keyboard(self, bot, chat_id, rcv_message = None):
        keyboard = []
        for item in self.m_list:
            keyboard.append(InlineKeyboardButton(item))
        
        self.bot = bot
        self.chat_id = chat_id
        
        if(rcv_message == None):
            message = self.__repr__()
        else:
            message = rcv_message
            
        reply_markup = telegram.ReplyKeyboardMarkup(self.build_menu(keyboard, n_cols=2))
        bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)  
        
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
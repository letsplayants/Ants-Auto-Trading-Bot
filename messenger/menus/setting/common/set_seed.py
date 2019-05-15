import json
import base64
import importlib
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from menus.menu_back import BackMenu
from menus.menu_item import MenuItem

from exchangem.crypto import Crypto
from env_server import Enviroments

STR_AVAL_SEED = '1회 최대 매매 금액'
STR_KEEP_SEED = '남겨둘 최소 금액'

class SetSeed(MenuItem):
    #API 등록 및 설정
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(AvailableSeed(exchange_name))
        self.__add__(KeepSeed(exchange_name))
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '거래 금액 설정'

    def to_dict(self):
        return '거래 금액 설정'
        
    def run(self):
        super().make_menu_keyboard(self.bot, self.chat_id, self.__get_msg__())
        
    def __get_msg__(self):
        try:
            available_seed = Enviroments().exchanges.get(self.exchange_name).get('coin').get('krw').get('amount').get('available')
            keep_seed = Enviroments().exchanges.get(self.exchange_name).get('coin').get('krw').get('amount').get('keep')
        except Exception as exp:
            raise Exception('거래 금액 설정 중 {} 거래소의 {} 설정이 없습니다.'.format(self.exchange_name, exp))
        
        msg = '{} : {}\n{} : {}'.format(STR_AVAL_SEED, available_seed, STR_KEEP_SEED, keep_seed)
        
        return msg
    
class AvailableSeed(MenuItem):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(BackMenu())
        self.init()
        pass
    
    def init(self):
        
        pass
    
    def back(self):
        Enviroments().save_config()
        self.dispatcher.remove_handler(self.test_mode_handler)
        self.dispatcher.remove_handler(self.fight_mode_handler)
        
    def __repr__(self):
        return STR_AVAL_SEED + ' 설정'
        
    def to_dict(self):
        return STR_AVAL_SEED + ' 설정'
    
    def __get_msg__(self):
        try:
            available_seed = Enviroments().exchanges.get(self.exchange_name).get('coin').get('krw').get('amount').get('available')
        except Exception as exp:
            raise Exception(exp)
        
        msg = '현재 {} : {}\n새롭게 설정하실 금액을 입력하세요.'.format(STR_AVAL_SEED, available_seed)
        
        return msg
        
    def edit_message(self, bot, query, msg):
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=msg)
        
    def run(self):
        msg = self.__get_msg__()
        super().make_menu_keyboard(self.bot, self.chat_id, msg)
    
    def parsering(self, update, context):
        self.logger.debug('got message : {}'.format(context))
        if(super().parsering(update, context)):
            self.logger.debug('got BACK BUTON message : {}'.format(context))
            return
        
        message = context.message
        text = message.text
        
        try:
            new_seed = float(text)
            msg = '새로 설정된 금액 : {}'.format(new_seed)
            Enviroments().exchanges[self.exchange_name]['coin']['krw']['amount']['available'] = new_seed
            Enviroments().save_config()
        except Exception as exp:
            self.logger.debug('exception : {}'.format(exp))
            msg = '올바른 숫자를 넣어주세요'
        
        super().make_menu_keyboard(self.bot, self.chat_id, msg)
        
class KeepSeed(MenuItem):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(BackMenu())
        self.init()
        pass
    
    def init(self):
        pass
    
    def back(self):
        Enviroments().save_config()
        self.dispatcher.remove_handler(self.test_mode_handler)
        self.dispatcher.remove_handler(self.fight_mode_handler)
        
    def __repr__(self):
        return STR_KEEP_SEED + ' 설정'
        
    def to_dict(self):
        return STR_KEEP_SEED + ' 설정'
        
    def __get_msg__(self):
        try:
            keep_seed = Enviroments().exchanges.get(self.exchange_name).get('coin').get('krw').get('amount').get('keep')
        except Exception as exp:
            raise Exception(exp)
        
        msg = '현재 {} : {}\n새롭게 설정하실 금액을 입력하세요.'.format(STR_KEEP_SEED, keep_seed)
        
        return msg
        
    def edit_message(self, bot, query, msg):
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=msg)
        
    def run(self):
        msg = self.__get_msg__()
        super().make_menu_keyboard(self.bot, self.chat_id, msg)
    
    def parsering(self, update, context):
        self.logger.debug('got message : {}'.format(context))
        if(super().parsering(update, context)):
            self.logger.debug('got BACK BUTON message : {}'.format(context))
            return
        
        message = context.message
        text = message.text
        
        try:
            new_seed = float(text)
            msg = '새로 설정된 금액 : {}'.format(new_seed)
            Enviroments().exchanges[self.exchange_name]['coin']['krw']['amount']['keep'] = new_seed
            Enviroments().save_config()
        except Exception as exp:
            self.logger.debug('exception : {}'.format(exp))
            msg = '올바른 숫자를 넣어주세요'
        
        super().make_menu_keyboard(self.bot, self.chat_id, msg)
        
if __name__ == "__main__":
    print('APIs test')
    
    import logging
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    # add = ApiAdd('upbit')
    # add.save_apikey()
    
    # print("\ucd5c\uc18c \uad6c\ub9e4\uc218\ub7c9\uc740 10 AE \uc785\ub2c8\ub2e4.")
    Enviroments().load_config()
    
    exc = Enviroments().exchanges
    if(exc is None or len(exc) is 0):
        print('error')
        
    # if(exc.get('upbit').get('traing_list').get('all')== True):
    #     print('all coin')
    
    pass

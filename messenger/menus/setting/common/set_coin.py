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

class SetCoinList(MenuItem):
    #API 등록 및 설정
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(CoinAdd(exchange_name))
        self.__add__(CoinDel(exchange_name))
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '자동 매매 코인 목록'

    def to_dict(self):
        return '자동 매매 코인 목록'
        
    def run(self):
        if(Enviroments().exchanges.get(self.exchange_name).get('trading_list').get('all') == True):
            msg = '{} 거래소 자동 매매  코인 목록 설정 목록 : \n{}'.format(self.exchange_name.upper(), '모든 코인')
        else:
            coin_list = Enviroments().exchanges.get(self.exchange_name).get('trading_list').get('list')
            if(len(coin_list) == 0):
                msg = '{} 거래소 자동 매매  코인 목록 설정 목록 : \n{}'.format(self.exchange_name.upper(), '없음')
            else:
                msg = '{} 거래소 자동 매매  코인 목록 설정 목록 : \n{}'.format(self.exchange_name.upper(), coin_list)
        
        super().make_menu_keyboard(self.bot, self.chat_id, msg)
        
    # def make_menu_keyboard(self, bot=None, chat_id=None, rcv_message = None):
    #     msg = '{} 거래소 자동 매매  코인 목록 설정 메뉴입니다'.format(self.exchange_name.upper())
    #     super().make_menu_keyboard(bot, chat_id, msg)
        
class CoinAdd(MenuItem):
    def __init__(self, exchange_name):
        super().__init__()
        self.exchange_name = exchange_name
        self.__add__(BackMenu())
        self.init()
        pass
    
    def init(self):
        self.test_mode_handler = CallbackQueryHandler(self.all_coin, pattern='all_coin')
        self.fight_mode_handler = CallbackQueryHandler(self.multi_coin, pattern='multi_coin')
        pass
    
    def back(self):
        Enviroments().save_config()
        self.dispatcher.remove_handler(self.test_mode_handler)
        self.dispatcher.remove_handler(self.fight_mode_handler)
        
        
    def __repr__(self):
        return '대상 코인 등록'
        
    def to_dict(self):
        return '대상 코인 등록'
    
    def __get_msg__(self):
        coins = ''
        if(Enviroments().exchanges.get(self.exchange_name).get('trading_list').get('all') == True):
            coins = '모든 코인'
        else:
            coin_list = Enviroments().exchanges.get(self.exchange_name).get('trading_list').get('list')
            if(len(coin_list) == 0):
                coins = '없음'
            else:
                coins = coin_list
        
        msg = """
        {} 거래소 자동 매매 코인 목록 설정
        모든 코인을 선택하려면 'ALLCOIN'을 입력하세요
        하나씩 선택하시려면 코인 심볼을 입력하세요(대소문자 안가림)
        예시) btc
        여러개를 선택하시려면 ,를 사용하여 구분하세요
        예시) btc, Eth, XRP
        
        현재 선택된 코인 : {}
        
        """.format(self.exchange_name.upper(), coins)
        
        return msg
        
    def all_coin(self, update, context):
        Enviroments().exchanges[self.exchange_name]['trading_list']['all'] = True
        Enviroments().save_config()
        
        query = context.callback_query
        user = query.from_user
        msg = self.__get_msg__()
        self.edit_message(update, query, msg)
    
    def multi_coin(self, update, context):
        Enviroments().exchanges[self.exchange_name]['trading_list']['all'] = False
        Enviroments().save_config()
        
        query = context.callback_query
        user = query.from_user
        msg = self.__get_msg__()
        self.edit_message(update, query, msg)
        
    def edit_message(self, bot, query, msg):
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=msg,
                        reply_markup=self.menu_keyboard())
        
    def run(self):
        self.dispatcher.add_handler(self.test_mode_handler)
        self.dispatcher.add_handler(self.fight_mode_handler)
        
        msg = self.__get_msg__()
        
        super().make_menu_keyboard(self.bot, self.chat_id, msg, reply_markup = self.menu_keyboard())
    
    def parsering(self, update, context):
        self.logger.debug('got message : {}'.format(context))
        if(super().parsering(update, context)):
            self.logger.debug('got BACK BUTON message : {}'.format(context))
            return
        
        message = context.message
        text = message.text
        add_list = []
        
        text_list = text.split(',')
        for item in text_list:
            item = item.strip().lower()
            clist = Enviroments().exchanges[self.exchange_name]['trading_list']['list']
            
            if item not in clist:
                clist.append(item)
                clist.sort()
                Enviroments().save_config()
                add_list.append(item)
            
        msg = '{} 추가됨'.format(add_list)
        super().make_menu_keyboard(self.bot, self.chat_id, msg)    
        
        
    def menu_keyboard(self):
        keyboard = [[InlineKeyboardButton("모든 코인 선택", callback_data='all_coin'),
                    InlineKeyboardButton("모든 코인 선택 해지", callback_data='multi_coin')]]
        
        return InlineKeyboardMarkup(keyboard)
        
class CoinDel(MenuItem):
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
        
    def __repr__(self):
        return '대상 코인 삭제'
        
    def to_dict(self):
        return '대상 코인 삭제'
    
    def __get_msg__(self):
        coins = ''
        coin_list = Enviroments().exchanges[self.exchange_name]['trading_list']['list']
        if(len(coin_list) == 0):
            coins = '없음'
        else:
            coins = coin_list
        
        msg = """
        코인이름을 넣으시면 삭제합니다.
        
        현재 남아있는 코인 : {}
        """.format(coins)
        
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
        del_list = []
        
        text_list = text.split(',')
        for item in text_list:
            item = item.strip().lower()
            clist = Enviroments().exchanges[self.exchange_name]['trading_list']['list']
            
            if item in clist:
                clist.remove(item)
                clist.sort()
                Enviroments().save_config()
                del_list.append(item)
            
        msg = '{} 삭제됨'.format(del_list)
        super().make_menu_keyboard(self.bot, self.chat_id, msg)    
        
        
    def menu_keyboard(self):
        keyboard = [[InlineKeyboardButton("모든 코인 선택", callback_data='all_coin'),
                    InlineKeyboardButton("모든 코인 선택 해지", callback_data='multi_coin')]]
        
        return InlineKeyboardMarkup(keyboard)
        
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

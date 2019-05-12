from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from menus.menu_back import BackMenu
from menus.menu_item import MenuItem

from env_server import Enviroments

class TestMode(MenuItem):
    def __init__(self):
        super().__init__()
        self.__add__(BackMenu())
        pass
        
    def __repr__(self):
        return '테스트모드 설정'
        
    def to_dict(self):
        return '테스트모드 설정'
        
    def init(self):
        self.test_mode_handler = CallbackQueryHandler(self.test_mode, pattern='test_mode')
        self.fight_mode_handler = CallbackQueryHandler(self.fight_mode, pattern='fight_mode')
        
        
    def back(self):
        self.dispatcher.remove_handler(self.test_mode_handler)
        self.dispatcher.remove_handler(self.fight_mode_handler)
        
    def test_mode(self, update, context):
        Enviroments().etc['test_mode'] = True
        Enviroments().save_config()
        query = context.callback_query
        user = query.from_user
        msg = '현재 모드 : {}'.format('테스트 모드')
        self.edit_message(update, query, msg)
    
    def fight_mode(self, update, context):
        Enviroments().etc['test_mode'] = False
        Enviroments().save_config()
        query = context.callback_query
        user = query.from_user
        msg = '현재 모드 : {}'.format('실전 모드')
        self.edit_message(update, query, msg)
        
    def edit_message(self, bot, query, msg):
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=msg,
                        reply_markup=self.menu_keyboard())
        
    def run(self):
        self.dispatcher.add_handler(self.test_mode_handler)
        self.dispatcher.add_handler(self.fight_mode_handler)
        
        if(Enviroments().etc['test_mode'] == True):
            message = '현재 모드 : {}'.format('테스트 모드')
        else:
            message = '현재 모드 : {}'.format('실전 모드')
        #1번 테스트 모드
        #2번 실전 모드
        super().make_menu_keyboard(self.bot, self.chat_id, message, reply_markup = self.menu_keyboard())
        
    def menu_func(self, update, context):
        context.message.reply_text('Please choose:', reply_markup=self.menu_keyboard())
        
    def menu_keyboard(self):
        keyboard = [[InlineKeyboardButton("테스트 모드", callback_data='test_mode'),
                    InlineKeyboardButton("실전 모드", callback_data='fight_mode')]]
        
        return InlineKeyboardMarkup(keyboard)
        
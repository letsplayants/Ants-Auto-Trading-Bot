from menus.menu_item import MenuItem
from menus.menu_back import BackMenu

from menus.trading.exchange.upbit import Upbit

class Trading(MenuItem):
    def __init__(self):
        super().__init__()
        self.__add__(Upbit())
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '거래'
    
    def to_dict(self):
        return '거래'
    
    def make_menu_keyboard(self, bot=None, chat_id=None, rcv_message = None):
        msg = '거래소를 선택하세요'
        super().make_menu_keyboard(bot, chat_id, msg)

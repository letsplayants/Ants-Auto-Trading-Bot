from menus.menu_item import MenuItem

from menus.setting.exchange.exchange import Exchange
from menus.back_menu import BackMenu
import logging

class Setting(MenuItem):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.__add__(Exchange())
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '설정'
    
    def to_dict(self):
        return '설정'
    
    

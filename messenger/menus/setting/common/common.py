from menus.menu_back import BackMenu
from menus.menu_item import MenuItem
from menus.setting.common.test_mode import TestMode
from menus.setting.common.set_coin import SetCoinList
from menus.setting.common.set_seed import SetSeed

class Common(MenuItem):
    def __init__(self):
        super().__init__()
        self.__add__(SetCoinList('default'))
        self.__add__(SetSeed('default'))
        self.__add__(TestMode())
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '일괄 설정'

    def to_dict(self):
        return '일괄 설정'
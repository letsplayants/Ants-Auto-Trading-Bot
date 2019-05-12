from menus.menu_back import BackMenu
from menus.menu_item import MenuItem
from menus.setting.etc.test_mode import TestMode

class Etc(MenuItem):
    def __init__(self):
        super().__init__()
        # self.__add__(TestMode())
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '기타 설정'

    def to_dict(self):
        return '기타 설정'
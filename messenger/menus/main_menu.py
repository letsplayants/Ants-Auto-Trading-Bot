import json

from menus.m_iter import MIterators
from menus.trading.trading import Trading
from menus.setting.setting import Setting
from menus.menu_back import BackMenu

class MainMenu(MIterators):
    def __init__(self):
        super().__init__()
        self.__add__(Trading())
        self.__add__(Setting())
        pass

    def __repr__(self):
        return '메인 메뉴'

    
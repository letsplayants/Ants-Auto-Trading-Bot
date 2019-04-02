import json

from menus.m_iter import MIterators
from menus.setting.setting import Setting
from menus.back_menu import BackMenu

class MainMenu(MIterators):
    def __init__(self):
        super().__init__()
        self.__add__(Setting())
        pass

    def __repr__(self):
        return '메인 메뉴'

    
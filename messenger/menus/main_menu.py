import json

from menus.m_iter import MIterators
from menus.setting.setting import Setting

class MainMenu(MIterators):
    def __init__(self):
        self.setting = Setting()
        self.__add__(self.setting)
        self.__add__(self.setting)
        pass

    def __repr__(self):
        return '메인 메뉴'

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)    
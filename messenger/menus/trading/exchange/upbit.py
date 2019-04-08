from menus.menu_item import MenuItem
from menus.menu_back import BackMenu

class Upbit(MenuItem):
    def __init__(self):
        super().__init__()
        # self.__add__(Trading())
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '업비트'
    
    def to_dict(self):
        return '업비트'
    
    

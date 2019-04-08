from menus.menu_item import MenuItem
from menus.menu_back import BackMenu

class Trading(MenuItem):
    def __init__(self):
        super().__init__()
        # self.__add__(CreateOrder)
        # self.__add__(ShowOrder)
        # self.__add__(CancelOrder)
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '거래'
    
    def to_dict(self):
        return '거래'
    
    
    
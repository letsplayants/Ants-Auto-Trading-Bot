from menus.menu_back import BackMenu
from menus.menu_item import MenuItem
from menus.setting.exchange.apis import ExchangeAPIs
from menus.setting.exchange.upbit import Upbit
from menus.setting.exchange.bithumb import Bithumb

class Exchange(MenuItem):
    def __init__(self):
        super().__init__()
        self.__add__(Upbit())
        self.__add__(Bithumb())
        # self.__add__(Binance())
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '거래소 설정'

    def to_dict(self):
        return '거래소 설정'
        

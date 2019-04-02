from menus.m_iter import MIterators
from menus.setting.exchange.apis import ExchangeAPIs
from menus.back_menu import BackMenu

class Exchange(MIterators):
    def __init__(self):
        super().__init__()
        self.__add__(ExchangeAPIs())
        self.__add__(BackMenu())
        pass
    
    def __repr__(self):
        return '거래소 설정'

    def to_dict(self):
        return '거래소 설정'
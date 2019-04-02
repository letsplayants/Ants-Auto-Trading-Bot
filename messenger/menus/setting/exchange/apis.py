from menus.m_iter import MIterators
from menus.back_menu import BackMenu

class ExchangeAPIs(MIterators):
    #API 등록 및 설정
    def __init__(self):
        super().__init__()
        self.__add__(ApiAdd())
        self.__add__(ApiTest())
        self.__add__(ApiDel())
        self.__add__(BackMenu())
        pass
    
    def __str__(self):
        return 'APIs key 설정'

    def to_dict(self):
        return 'APIs Key 설정'
        
class ApiAdd:
    def to_dict(self):
        return 'API Key 등록'
    pass

class ApiTest:
    def to_dict(self):
        return 'API Key 테스트'
    pass

class ApiDel:
    def to_dict(self):
        return 'API Key 삭제'
    pass

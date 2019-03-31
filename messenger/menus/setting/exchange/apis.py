from menus.m_iter import MIterators

class ExchangeAPIs(MIterators):
    #API 등록 및 설정
    def __init__(self):
        self.__add__(self.add)
        self.__add__(self.test)
        self.__add__(self.delete)
        pass
    
    def __str__(self):
        return 'APIs key 등록/테스트/삭제'


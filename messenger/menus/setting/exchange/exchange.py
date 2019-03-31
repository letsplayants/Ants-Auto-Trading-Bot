from menus.m_iter import MIterators

class Exchange(MIterators):
    #API 등록 및 설정
    def __init__(self):
        self.__add__(self.setting)
        self.__add__(self.setting)
        
        pass
    
    def __str__(self):
        return '거래소 설정'
